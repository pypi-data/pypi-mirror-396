use anyhow::{bail, Context, Result};
use bytes::Bytes;
use futures_util::{SinkExt, StreamExt};
use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::PyBytes;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::net::SocketAddr;
use std::sync::Arc;
use tokio::net::{TcpListener, TcpStream};
use tokio::sync::{mpsc, Mutex, RwLock};
use tokio_util::codec::{Framed, LengthDelimitedCodec};

macro_rules! vprintln {
    ($v:expr, $($t:tt)*) => { if $v { println!($($t)*); } };
}

/* ----------------------------- wire messages ---------------------------- */

#[derive(Debug, Serialize, Deserialize)]
enum Msg {
    Hello { idx: Option<usize> },
    Start { n: usize, your_idx: usize },
    DataTo { to: Option<usize>, tag: Option<String>, payload: Vec<u8> }, // client -> hub
    DataFrom { from: usize, tag: Option<String>, payload: Vec<u8> },     // hub -> client
    Close,
}

/* Helpers for split sink/stream */

type FramedSink = futures_util::stream::SplitSink<Framed<TcpStream, LengthDelimitedCodec>, Bytes>;
type FramedStream = futures_util::stream::SplitStream<Framed<TcpStream, LengthDelimitedCodec>>;

async fn send_msg_sink(sink: &mut FramedSink, msg: &Msg) -> Result<()> {
    let bytes = bincode::serialize(msg)?;
    sink.send(Bytes::from(bytes)).await?;
    Ok(())
}
async fn recv_msg_stream(stream: &mut FramedStream) -> Result<Msg> {
    let frame = stream.next().await.context("connection closed")??;
    Ok(bincode::deserialize(&frame)?)
}

/* ----------------------------- coordinator ----------------------------- */

type PeerTx = mpsc::Sender<Msg>;

#[derive(Clone)]
struct Hub {
    peers: Arc<RwLock<HashMap<usize, PeerTx>>>,
    inbound: mpsc::Sender<Inbound>,
    verbose: bool,
    n: usize,
}

#[derive(Debug)]
struct Inbound {
    from: usize,
    tag: Option<String>,
    payload: Vec<u8>,
}

async fn serve_coordinator(
    bind: String,
    n: usize,
    verbose: bool,
    ready_tx: mpsc::Sender<()>,
    inbound_tx: mpsc::Sender<Inbound>,
    peers_shared: Arc<RwLock<HashMap<usize, PeerTx>>>,
) -> Result<()> {
    let hub = Hub {
        peers: peers_shared,
        inbound: inbound_tx,
        verbose,
        n,
    };

    let listener = TcpListener::bind(&bind).await?;
    vprintln!(verbose, "[hub] listening on {}", bind);

    loop {
        let (sock, _addr) = listener.accept().await?;
        //let framed = Framed::new(sock, LengthDelimitedCodec::new());
        let codec = LengthDelimitedCodec::builder()
            .max_frame_length(268_435_456) // 256 MiB
            .new_codec();

        let framed = Framed::new(sock, codec);
        let (mut sink, mut stream) = framed.split();
        let hub_accept = hub.clone();

        // handshake: expect Hello, then assign index
        let assigned_idx = match recv_msg_stream(&mut stream).await? {
            Msg::Hello { idx } => {
                if let Some(want) = idx {
                    if want >= hub_accept.n || hub_accept.peers.read().await.contains_key(&want) {
                        bail!("invalid or duplicate idx requested: {}", want);
                    }
                    want
                } else {
                    // first free slot
                    let peers = hub_accept.peers.read().await;
                    let mut i = 0usize;
                    while peers.contains_key(&i) { i += 1; }
                    drop(peers);
                    if i >= hub_accept.n { bail!("all {} party slots filled", hub_accept.n); }
                    i
                }
            }
            _ => bail!("expected Hello"),
        };

        // per-peer outbound queue
        let (ptx, mut prx) = mpsc::channel::<Msg>(64);
        {
            let mut peers = hub_accept.peers.write().await;
            peers.insert(assigned_idx, ptx.clone());
            if peers.len() == hub_accept.n {
                let _ = ready_tx.send(()).await; // signal "ready" once N are connected
            }
        }

        // send Start
        send_msg_sink(&mut sink, &Msg::Start { n: hub_accept.n, your_idx: assigned_idx }).await?;

        // writer task (hub -> this client)
        let mut sink_writer = sink;
        let verbose_w = hub_accept.verbose;
        tokio::spawn(async move {
            while let Some(msg) = prx.recv().await {
                let _ = send_msg_sink(&mut sink_writer, &msg).await;
            }
            vprintln!(verbose_w, "[hub] writer for {} closed", assigned_idx);
        });

        // reader task (client -> hub)
        let mut stream_reader = stream;
        let hub_reader = hub_accept.clone();
        tokio::spawn(async move {
            loop {
                match recv_msg_stream(&mut stream_reader).await {
                    Ok(Msg::DataTo { to, tag, payload }) => {
                        match to {
                            Some(dest) => {
                                // forward to destination party
                                let peers = hub_reader.peers.read().await;
                                if let Some(tx) = peers.get(&dest) {
                                    let _ = tx.send(Msg::DataFrom { from: assigned_idx, tag, payload }).await;
                                }
                            }
                            None => {
                                // deliver to coordinator inbox
                                let _ = hub_reader.inbound.send(Inbound { from: assigned_idx, tag, payload }).await;
                            }
                        }
                    }
                    Ok(Msg::Close) => break,
                    Ok(_) => {}
                    Err(_) => break,
                }
            }
            // cleanup
            let mut peers = hub_reader.peers.write().await;
            peers.remove(&assigned_idx);
            vprintln!(hub_reader.verbose, "[hub] party {} disconnected", assigned_idx);
        });
    }
}

/* ----------------------- Python-visible Coordinator --------------------- */

#[pyclass]
struct Coordinator {
    peers: Arc<RwLock<HashMap<usize, PeerTx>>>,
    rx: Arc<Mutex<mpsc::Receiver<Inbound>>>,
    verbose: bool,
    n: usize,
}

#[pymethods]
impl Coordinator {
    #[getter]
    fn n(&self) -> usize { self.n }

    fn __repr__(&self) -> String {
        format!("<Coordinator n={} verbose={}>", self.n, self.verbose)
    }

    /// Await a message sent to the coordinator. Returns (from_idx, tag, obj)
    fn recv<'p>(&self, py: Python<'p>) -> PyResult<&'p PyAny> {
        let rx = self.rx.clone();
        pyo3_asyncio::tokio::future_into_py(py, async move {
            let mut guard = rx.lock().await;
            let inbox = guard.recv().await.ok_or_else(|| PyRuntimeError::new_err("coordinator closed"))?;
            Python::with_gil(|py| {
                let pickle = py.import("pickle")?;
                let obj = pickle.call_method1("loads", (PyBytes::new(py, &inbox.payload),))?;
                // build a Python tuple explicitly
                Ok::<PyObject, PyErr>((inbox.from, inbox.tag, obj).to_object(py))
            })
        })
    }

    /// Send an object to a specific party.
    #[pyo3(signature = (to, obj, *, tag=None))]
    fn send<'p>(&self, py: Python<'p>, to: usize, obj: &PyAny, tag: Option<String>) -> PyResult<&'p PyAny> {
        let peers = self.peers.clone();
        let verbose = self.verbose;
        // pickle payload now
        let payload: Vec<u8> = {
            let pickle = py.import("pickle")?;
            let proto: i32 = pickle.getattr("HIGHEST_PROTOCOL")?.extract()?;
            let b: &PyAny = pickle.call_method1("dumps", (obj, proto))?;
            b.extract()?
        };
        pyo3_asyncio::tokio::future_into_py(py, async move {
            let peers_guard = peers.read().await;
            match peers_guard.get(&to) {
                Some(tx) => {
                    let _ = tx.send(Msg::DataFrom { from: usize::MAX, tag, payload }).await;
                    if verbose { println!("[hub] sent -> {}", to); }
                    Ok(())
                }
                None => Err(PyValueError::new_err(format!("destination {} not connected", to))),
            }
        })
    }

    /// Broadcast an object to all connected parties.
    #[pyo3(signature = (obj, *, tag=None))]
    fn broadcast<'p>(&self, py: Python<'p>, obj: &PyAny, tag: Option<String>) -> PyResult<&'p PyAny> {
        let peers = self.peers.clone();
        let verbose = self.verbose;
        let payload: Vec<u8> = {
            let pickle = py.import("pickle")?;
            let proto: i32 = pickle.getattr("HIGHEST_PROTOCOL")?.extract()?;
            let b: &PyAny = pickle.call_method1("dumps", (obj, proto))?;
            b.extract()?
        };
        pyo3_asyncio::tokio::future_into_py(py, async move {
            let peers_guard = peers.read().await;
            for (idx, tx) in peers_guard.iter() {
                let _ = tx.send(Msg::DataFrom { from: usize::MAX, tag: tag.clone(), payload: payload.clone() }).await;
                if verbose { println!("[hub] broadcast -> {}", idx); }
            }
            Ok(())
        })
    }
}

/* --------------------------- Python-visible Party ----------------------- */

#[pyclass]
struct Party {
    tx: mpsc::Sender<Msg>, // to hub
    rx: Arc<Mutex<mpsc::Receiver<(usize, Option<String>, Vec<u8>)>>>, // from hub
    idx: usize,
    verbose: bool,
}

#[pymethods]
impl Party {
    #[getter]
    fn idx(&self) -> usize { self.idx }

    fn __repr__(&self) -> String {
        format!("<Party idx={} verbose={}>", self.idx, self.verbose)
    }

    /// Send an object. to=None -> coordinator; to=<idx> -> another party.
    #[pyo3(signature = (obj, *, to=None, tag=None))]
    fn send<'p>(&self, py: Python<'p>, obj: &PyAny, to: Option<usize>, tag: Option<String>) -> PyResult<&'p PyAny> {
        let tx = self.tx.clone();
        let verbose = self.verbose;
        let payload: Vec<u8> = {
            let pickle = py.import("pickle")?;
            let proto: i32 = pickle.getattr("HIGHEST_PROTOCOL")?.extract()?;
            let b: &PyAny = pickle.call_method1("dumps", (obj, proto))?;
            b.extract()?
        };
        pyo3_asyncio::tokio::future_into_py(py, async move {
            let _ = tx.send(Msg::DataTo { to, tag, payload }).await;
            if verbose {
                match to { Some(t) => println!("[party] sent -> {}", t), None => println!("[party] sent -> coordinator") }
            }
            Ok(())
        })
    }

    /// Receive a message. Returns (from_idx, tag, obj)
    fn recv<'p>(&self, py: Python<'p>) -> PyResult<&'p PyAny> {
        let rx = self.rx.clone();
        pyo3_asyncio::tokio::future_into_py(py, async move {
            let mut guard = rx.lock().await;
            let (from, tag, payload) = guard.recv().await.ok_or_else(|| PyRuntimeError::new_err("party connection closed"))?;
            Python::with_gil(|py| {
                let pickle = py.import("pickle")?;
                let obj = pickle.call_method1("loads", (PyBytes::new(py, &payload),))?;
                Ok::<PyObject, PyErr>((from, tag, obj).to_object(py))
            })
        })
    }

    /// Optional graceful close.
    fn close<'p>(&self, _py: Python<'p>) -> PyResult<&'p PyAny> {
        let tx = self.tx.clone();
        pyo3_asyncio::tokio::future_into_py(_py, async move {
            let _ = tx.send(Msg::Close).await;
            Ok(())
        })
    }
}

/* ------------------------------- entry points -------------------------- */

fn pyerr<E: ToString>(e: E) -> PyErr { PyRuntimeError::new_err(e.to_string()) }

#[pyfunction]
#[pyo3(signature = (bind, n, *, verbose=false))]
fn start_coordinator(py: Python<'_>, bind: String, n: usize, verbose: bool) -> PyResult<&PyAny> {
    pyo3_asyncio::tokio::future_into_py(py, async move {
        let (ready_tx, mut ready_rx) = mpsc::channel::<()>(1);
        let (in_tx, in_rx) = mpsc::channel::<Inbound>(1024);
        let peers_shared: Arc<RwLock<HashMap<usize, PeerTx>>> = Arc::new(RwLock::new(HashMap::new()));
        let peers_for_handle = peers_shared.clone();

        let bind_clone = bind.clone();
        tokio::spawn(async move {
            if let Err(e) = serve_coordinator(bind_clone, n, verbose, ready_tx, in_tx, peers_shared).await {
                eprintln!("[hub] error: {}", e);
            }
        });

        // wait until the first "ready" (when N are connected)
        let _ = ready_rx.recv().await;

        Python::with_gil(|py| {
            let coord = Coordinator {
                peers: peers_for_handle,
                rx: Arc::new(Mutex::new(in_rx)),
                verbose,
                n,
            };
            Py::new(py, coord)
        }).map_err(pyerr)
    })
}

#[pyfunction]
#[pyo3(signature = (connect, idx=None, *, verbose=false))]
fn connect_party(py: Python<'_>, connect: String, idx: Option<usize>, verbose: bool) -> PyResult<&PyAny> {
    pyo3_asyncio::tokio::future_into_py(py, async move {
        let addr: SocketAddr = connect.parse().map_err(pyerr)?;
        let sock = TcpStream::connect(addr).await.map_err(pyerr)?;
        //let framed = Framed::new(sock, LengthDelimitedCodec::new());
        let codec = LengthDelimitedCodec::builder()
            .max_frame_length(268_435_456) // 256 MiB
            .new_codec();

        let framed = Framed::new(sock, codec);
        let (mut sink, mut stream) = framed.split();

        // hello
        send_msg_sink(&mut sink, &Msg::Hello { idx }).await.map_err(pyerr)?;

        // expect Start
        let your_idx = match recv_msg_stream(&mut stream).await.map_err(pyerr)? {
            Msg::Start { your_idx, .. } => your_idx,
            _ => return Err(pyerr("expected Start")),
        };

        // inbound channel (hub -> party)
        let (in_tx, in_rx) = mpsc::channel::<(usize, Option<String>, Vec<u8>)>(1024);

        // reader
        tokio::spawn(async move {
            let mut reader = stream;
            loop {
                match recv_msg_stream(&mut reader).await {
                    Ok(Msg::DataFrom { from, tag, payload }) => {
                        let _ = in_tx.send((from, tag, payload)).await;
                    }
                    Ok(Msg::Close) => break,
                    Ok(_) => {}
                    Err(_) => break,
                }
            }
        });

        // sender (party -> hub)
        let (out_tx, mut out_rx) = mpsc::channel::<Msg>(64);
        tokio::spawn(async move {
            let mut writer = sink;
            while let Some(msg) = out_rx.recv().await {
                let _ = send_msg_sink(&mut writer, &msg).await;
            }
        });

        Python::with_gil(|py| {
            let party = Party {
                tx: out_tx,
                rx: Arc::new(Mutex::new(in_rx)),
                idx: your_idx,
                verbose,
            };
            Py::new(py, party)
        }).map_err(pyerr)
    })
}

#[pymodule]
fn mpc_py(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(start_coordinator, m)?)?;
    m.add_function(wrap_pyfunction!(connect_party, m)?)?;
    Ok(())
}

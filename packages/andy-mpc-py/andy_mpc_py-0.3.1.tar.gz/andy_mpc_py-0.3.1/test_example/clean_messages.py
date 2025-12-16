# clean_messages.py
import asyncio
from typing import Optional, List, Tuple, Any
from mpc_py import start_coordinator, connect_party

BIND = "127.0.0.1:5000"
COORD_ID = (1 << 64) - 1  # internal id for coordinator

# -----------------------------
# Coordinator (one-shot broadcast, then keepalive)
# -----------------------------
async def run_coordinator():
    coord = await start_coordinator(BIND, n=2)
    print("[Coordinator] ready")

    await coord.broadcast({"kind": "init", "msg": "hello both — start whenever you like"}, tag="init")
    print("[Coordinator] sent init; staying alive to route traffic")

    try:
        await asyncio.Event().wait()  # keep routing until Ctrl-C
    except (KeyboardInterrupt, SystemExit):
        print("[Coordinator] shutting down")

# -----------------------------
# Party logic (works for both)
# -----------------------------
async def party_loop(idx: int):
    party = await connect_party(BIND, idx=idx)
    me = f"party-{idx+1}"
    peer_idx = 1 - idx
    peer_name = f"party-{peer_idx+1}"
    print(f"[{me}] connected")

    # Buffer for messages we saw but haven't consumed yet
    pending: List[Tuple[int, Optional[str], Any]] = []

    # (A) Wait for coordinator's single INIT *before* starting any rounds.
    # This prevents the racy "first message arrives before peer is listening".
    await wait_for_init(party, pending)
    print(f"[{me}] got coordinator init; ready for rounds with {peer_name}")

    # (B) Normal rounds (no for-loop; explicit calls)
    await run_round(party, me, peer_idx, peer_name, r=1, pending=pending, msg=f"hi {peer_name} (r1)")
    await run_round(party, me, peer_idx, peer_name, r=2, pending=pending, msg=f"hi again {peer_name} (r2)")
    await run_round(party, me, peer_idx, peer_name, r=3, pending=pending, msg=f"last one {peer_name} (r3)")

    print(f"[{me}] finished")

# -----------------------------
# Helpers
# -----------------------------
async def wait_for_init(party, pending: List[Tuple[int, Optional[str], Any]], timeout: float = 30.0):
    """Block until we see the coordinator's one-shot init; buffer anything else."""
    deadline = asyncio.get_event_loop().time() + timeout
    while True:
        remaining = deadline - asyncio.get_event_loop().time()
        if remaining <= 0:
            raise TimeoutError("timed out waiting for coordinator init")

        frm, tag, obj = await asyncio.wait_for(party.recv(), timeout=remaining)
        # Debug: show every message
        # print(f"[debug] during init wait: frm={frm} tag={tag} obj={obj}")

        if frm == COORD_ID and tag == "init" and isinstance(obj, dict) and obj.get("kind") == "init":
            # got the one-shot init
            return
        else:
            # keep for later (e.g., peer early messages)
            pending.append((frm, tag, obj))

async def recv_matching_with_pending(
    party,
    *,
    want_round: int,
    want_from_name: str,
    pending: List[Tuple[int, Optional[str], Any]],
    recv_timeout: Optional[float],
):
    """Pop a matching message from pending if present; otherwise keep receiving, buffering non-matches."""
    # First, scan pending
    for i, (frm, tag, obj) in enumerate(pending):
        if (
            isinstance(obj, dict)
            and obj.get("kind") == "peer-msg"
            and obj.get("round") == want_round
            and obj.get("from") == want_from_name
        ):
            pending.pop(i)
            return frm, tag, obj

    # Then, read from the wire until we get what we want
    while True:
        try:
            if recv_timeout is None:
                frm, tag, obj = await party.recv()
            else:
                frm, tag, obj = await asyncio.wait_for(party.recv(), timeout=recv_timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(f"timed out waiting for {want_from_name}'s message for round {want_round}")
        except RuntimeError as e:
            raise RuntimeError("connection dropped while waiting for message") from e

        print(f"[debug] saw message: frm={frm} tag={tag} obj={obj}")

        if (
            isinstance(obj, dict)
            and obj.get("kind") == "peer-msg"
            and obj.get("round") == want_round
            and obj.get("from") == want_from_name
        ):
            return frm, tag, obj
        else:
            pending.append((frm, tag, obj))

# -----------------------------
# Round
# -----------------------------
async def run_round(
    party,
    me: str,
    peer_idx: int,
    peer_name: str,
    r: int,
    *,
    pending: List[Tuple[int, Optional[str], Any]],
    msg: Optional[str] = None,
    recv_timeout: Optional[float] = 30.0,
):
    """Single round r: send once, then wait for peer's message for r (with pending-buffer)."""
    if msg is None:
        msg = f"hello {peer_name} (r{r})"

    # Send to peer
    await party.send({"kind": "peer-msg", "round": r, "from": me, "msg": msg}, to=peer_idx)
    print(f"[{me}] round {r}: sent to {peer_name}: {msg}")

    # Receive the peer's r message (using the pending buffer)
    frm, tag, obj = await recv_matching_with_pending(
        party,
        want_round=r,
        want_from_name=peer_name,
        pending=pending,
        recv_timeout=recv_timeout,
    )
    print(f"[{me}] round {r}: from {peer_name}: {obj['msg']}")
    return obj

# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--role", choices=["coord", "p1", "p2"], required=True)
    args = ap.parse_args()

    if args.role == "coord":
        asyncio.run(run_coordinator())
    elif args.role == "p1":
        asyncio.run(party_loop(0))
    elif args.role == "p2":
        asyncio.run(party_loop(1))

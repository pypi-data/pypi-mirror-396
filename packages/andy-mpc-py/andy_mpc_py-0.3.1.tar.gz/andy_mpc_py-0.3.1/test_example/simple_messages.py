# simple_messages.py
import asyncio
from mpc_py import start_coordinator, connect_party

BIND = "127.0.0.1:5000"
ROUNDS = 3
COORD_ID = (1 << 64) - 1  # internal id for coordinator

def who(frm: int) -> str:
    return "coordinator" if frm == COORD_ID else f"party-{frm+1}"

async def recv_until(endpoint, predicate, timeout=None):
    """Receive messages until predicate(frm, tag, obj) returns a non-None value; return that value."""
    while True:
        frm, tag, obj = await asyncio.wait_for(endpoint.recv(), timeout=timeout)
        out = predicate(frm, tag, obj)
        if out is not None:
            return out

# -----------------------------
# Coordinator (barrier + rounds)
# -----------------------------
async def run_coordinator():
    coord = await start_coordinator(BIND, n=2)
    print("[Coordinator] ready")

    for r in range(1, ROUNDS + 1):
        print(f"[Coordinator] round {r}: GO")
        # tell both parties to start round r
        await coord.broadcast({"kind": "go", "round": r}, tag="go")

        # optional: also send them a one-way message this round
        await coord.send(0, {"kind": "from-coord", "round": r, "msg": f"hi p1 (r{r})"})
        await coord.send(1, {"kind": "from-coord", "round": r, "msg": f"hi p2 (r{r})"})

        # wait for both acks
        got = set()
        while len(got) < 2:
            frm, tag, obj = await coord.recv()
            if isinstance(obj, dict) and obj.get("kind") == "done" and obj.get("round") == r:
                got.add(frm)
                print(f"[Coordinator] got done from {who(frm)} for round {r}")
        print(f"[Coordinator] round {r}: ALL DONE\n")

    print("[Coordinator] finished")

# -----------------------------
# Party logic (works for both)
# -----------------------------
async def party_loop(idx: int):
    party = await connect_party(BIND, idx=idx)
    me = f"party-{idx+1}"
    peer_idx = 1 - idx
    peer_name = f"party-{peer_idx+1}"
    print(f"[{me}] connected")

    for r in range(1, ROUNDS + 1):
        # wait for coordinator's GO for this round
        await recv_until(
            party,
            lambda frm, tag, obj:
                obj if (frm == COORD_ID and isinstance(obj, dict) and obj.get("kind") == "go" and obj.get("round") == r) else None,
            timeout=None,
        )
        print(f"[{me}] round {r}: GO received")

        # send to the peer
        await party.send({"kind": "peer-msg", "round": r, "from": me, "msg": f"hello {peer_name} (r{r})"}, to=peer_idx)

        # also consume the coordinator's one-way message (if any) without blocking the round:
        # we’ll accept either the peer message or coord message first, then keep reading until
        # we’ve seen the peer message for this round.
        got_peer = False
        while not got_peer:
            frm, tag, obj = await party.recv()
            if isinstance(obj, dict) and obj.get("round") == r:
                if obj.get("kind") == "peer-msg" and frm == peer_idx:
                    print(f"[{me}] round {r}: from {peer_name}: {obj['msg']}")
                    got_peer = True
                elif frm == COORD_ID and obj.get("kind") == "from-coord":
                    print(f"[{me}] round {r}: from coordinator: {obj['msg']}")
                # ignore anything else (tags from earlier/later rounds)

        # tell coordinator we’re done with this round
        await party.send({"kind": "done", "round": r})

    print(f"[{me}] finished")

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

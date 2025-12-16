# two_party_add.py
import asyncio
import secrets
from typing import Optional, List, Tuple, Any
from mpc_py import start_coordinator, connect_party

BIND = "127.0.0.1:5000"
COORD_ID = (1 << 64) - 1  # internal id for coordinator

# -----------------------------
# Coordinator (one-shot init, then keepalive router)
# -----------------------------
async def run_coordinator():
    coord = await start_coordinator(BIND, n=2)
    print("[Coordinator] ready")
    await coord.broadcast({"kind": "init"}, tag="init")
    print("[Coordinator] init sent; routing (Ctrl-C to stop)")
    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        print("[Coordinator] shutting down")

# -----------------------------
# Party entry
# -----------------------------
async def run_party(idx: int, value: int, mod: int):
    """
    Two-party addition over Z_mod.
    idx=0 holds x, idx=1 holds y. Each learns z = (x+y) mod mod.
    """
    party = await connect_party(BIND, idx=idx)
    me = f"party-{idx+1}"
    peer_idx = 1 - idx
    peer_name = f"party-{peer_idx+1}"

    # Local buffer so early/out-of-order messages aren't lost
    pending: List[Tuple[int, Optional[str], Any]] = []

    # Wait for coordinator's single init (prevents first-message races)
    await wait_for_init(party, pending)

    # ===== Round 1: exchange random masks r1, r2 =====
    my_r = secrets.randbits(128) % mod  # wide randomness then reduce mod
    await party.send({"kind": "mask", "from": me, "r": my_r}, to=peer_idx)

    _, _, peer_mask_msg = await recv_matching_with_pending(
        party,
        want_kind="mask",
        want_from=peer_name,
        pending=pending,
        recv_timeout=30.0,
    )
    peer_r = int(peer_mask_msg["r"])

    # Local additive share of the sum
    # P1: s1 = x - r1 + r2   (mod M)
    # P2: s2 = y - r2 + r1   (mod M)
    my_share = (value - my_r + peer_r) % mod

    # ===== Round 2: exchange shares, reconstruct =====
    await party.send({"kind": "sum-share", "from": me, "share": my_share}, to=peer_idx)

    _, _, peer_share_msg = await recv_matching_with_pending(
        party,
        want_kind="sum-share",
        want_from=peer_name,
        pending=pending,
        recv_timeout=30.0,
    )
    peer_share = int(peer_share_msg["share"])

    z = (my_share + peer_share) % mod

    # Output only the final result (clean, MPC-style)
    role = "x" if idx == 0 else "y"
    print(f"[{me}] input {role} set. Result (x + y) mod {mod} = {z}")

# -----------------------------
# Small helpers (buffer + matching)
# -----------------------------
async def wait_for_init(party, pending: List[Tuple[int, Optional[str], Any]], timeout: float = 30.0):
    deadline = asyncio.get_event_loop().time() + timeout
    while True:
        remaining = deadline - asyncio.get_event_loop().time()
        if remaining <= 0:
            raise TimeoutError("timed out waiting for coordinator init")
        frm, tag, obj = await asyncio.wait_for(party.recv(), timeout=remaining)
        if frm == COORD_ID and tag == "init" and isinstance(obj, dict) and obj.get("kind") == "init":
            return
        pending.append((frm, tag, obj))  # buffer anything else

async def recv_matching_with_pending(
    party,
    *,
    want_kind: str,
    want_from: str,
    pending: List[Tuple[int, Optional[str], Any]],
    recv_timeout: Optional[float],
):
    # First, scan pending
    for i, (frm, tag, obj) in enumerate(pending):
        if isinstance(obj, dict) and obj.get("kind") == want_kind and obj.get("from") == want_from:
            return pending.pop(i)
    # Then, receive until match
    while True:
        try:
            frm, tag, obj = await (party.recv() if recv_timeout is None
                                   else asyncio.wait_for(party.recv(), timeout=recv_timeout))
        except asyncio.TimeoutError:
            raise TimeoutError(f"timed out waiting for {want_from}'s {want_kind}")
        except RuntimeError as e:
            raise RuntimeError("connection dropped while waiting for message") from e

        if isinstance(obj, dict) and obj.get("kind") == want_kind and obj.get("from") == want_from:
            return (frm, tag, obj)
        pending.append((frm, tag, obj))

# -----------------------------
# CLI
# -----------------------------
if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Two-party addition via additive secret sharing")
    ap.add_argument("--role", choices=["coord", "p1", "p2"], required=True)
    ap.add_argument("--value", type=int, help="Private value (x for p1, y for p2). Required for parties.")
    ap.add_argument("--mod", type=int, default=2**64, help="Modulus M (default 2^64)")
    args = ap.parse_args()

    if args.role == "coord":
        asyncio.run(run_coordinator())
    else:
        if args.value is None:
            raise SystemExit("Error: --value is required for p1/p2")
        idx = 0 if args.role == "p1" else 1
        asyncio.run(run_party(idx=idx, value=args.value, mod=args.mod))

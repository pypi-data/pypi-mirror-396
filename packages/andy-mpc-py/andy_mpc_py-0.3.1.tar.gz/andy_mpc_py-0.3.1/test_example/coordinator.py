# coordinator.py
import argparse
import asyncio
from mpc_py import start_coordinator

async def main():
    ap = argparse.ArgumentParser("pipe coordinator")
    ap.add_argument("--bind", default="127.0.0.1:5000")
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    coord = await start_coordinator(args.bind, args.n, verbose=args.verbose)
    # echo/broadcast loop (example): any message to coordinator is broadcast to all
    while True:
        frm, tag, obj = await coord.recv()
        # quiet by default; print nothing. Uncomment if you want to see traffic:
        # print(f"[coord] from={frm} tag={tag} type={type(obj)}")
        await coord.broadcast(obj, tag=tag)

if __name__ == "__main__":
    asyncio.run(main())

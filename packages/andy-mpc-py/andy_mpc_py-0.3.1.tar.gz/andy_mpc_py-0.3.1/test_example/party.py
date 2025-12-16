# party.py
import argparse
import asyncio
import json
from typing import Any
from mpc_py import connect_party

def parse_value(s: str) -> Any:
    # accept numbers or JSON (lists/dicts); numpy/torch objects can be passed via --pyexpr
    try:
        return json.loads(s)
    except Exception:
        try:
            if any(c in s for c in ".eE"):
                return float(s)
            return int(s)
        except Exception:
            return s  # plain string fallback

async def main():
    ap = argparse.ArgumentParser("pipe party")
    ap.add_argument("--connect", default="127.0.0.1:5000")
    ap.add_argument("--idx", type=int, default=None)
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--to", type=int, default=None, help="destination idx (None -> coordinator)")
    ap.add_argument("--tag", default=None)
    ap.add_argument("--value", help="number or JSON string (for lists/dicts/matrices)")
    ap.add_argument("--pyexpr", default=None,
        help="Python expression evaluated and sent as the payload (e.g., 'np.arange(6).reshape(2,3)')")
    args = ap.parse_args()

    # optional: build complex objects with numpy/torch
    payload = parse_value(args.value) if args.value is not None else None
    if args.pyexpr is not None:
        ns = {}
        try:
            import numpy as np  # noqa
            ns["np"] = np
        except Exception:
            pass
        try:
            import torch  # noqa
            ns["torch"] = torch
        except Exception:
            pass
        payload = eval(args.pyexpr, ns, {})

    party = await connect_party(args.connect, idx=args.idx, verbose=args.verbose)
    if payload is not None:
        await party.send(payload, to=args.to, tag=args.tag)

    # Example receive loop (optional). Comment out if you don't want to listen.
    # while True:
    #     frm, tag, obj = await party.recv()
    #     print(f"[party {party.idx}] from={frm} tag={tag} type={type(obj)} value={str(obj)[:60]}")

if __name__ == "__main__":
    asyncio.run(main())

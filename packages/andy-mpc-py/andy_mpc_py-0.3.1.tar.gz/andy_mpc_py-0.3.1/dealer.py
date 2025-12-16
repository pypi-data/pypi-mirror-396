import asyncio
import secrets
from typing import Optional, List, Tuple, Any
from mpc_py import start_coordinator, connect_party

BIND = "127.0.0.1:5000"
COORD_ID = (1 << 64) - 1  # internal id for coordinator

async def main():
    coord = await start_coordinator(BIND, n=2)
    print("[Coordinator] ready")
    await coord.broadcast({"kind": "init"}, tag="init")
    print("[Coordinator] init sent; routing (Ctrl-C to stop)")
    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        print("[Coordinator] shutting down")

if __name__ == "__main__":
    asyncio.run(main())
"""Real-time order book streaming via WebSocket.

Subscribes to order book updates (S01) and displays
the bid-ask spread.

Requires: pip install pydbsec[ws]
"""

import asyncio

from pydbsec import AsyncPyDBSec


async def main():
    async with AsyncPyDBSec(
        app_key="YOUR_APP_KEY",
        app_secret="YOUR_APP_SECRET",
    ) as client:
        async with client.ws as ws:
            # Subscribe to Samsung orderbook
            await ws.subscribe("005930", tr_code="S01")

            print("Streaming 005930 order book... (Ctrl+C to stop)\n")

            async for msg in ws:
                if msg.tr_code != "S01":
                    continue

                data = msg.data if isinstance(msg.data, dict) else {}
                print(f"[{data.get('timestamp', '')}] 005930 Order Book Update")

                # Display bid-ask if available
                for key in sorted(data.keys()):
                    if "Ask" in key or "Bid" in key:
                        print(f"  {key}: {data[key]}")
                print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped.")

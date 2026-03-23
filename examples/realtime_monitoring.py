"""Real-time price monitoring via WebSocket.

Subscribes to execution data (S00) for multiple stocks
and prints incoming ticks. Ctrl+C to stop.

Requires: pip install pydbsec[ws]
"""

import asyncio
import signal

from pydbsec import AsyncPyDBSec


async def main():
    async with AsyncPyDBSec(
        app_key="YOUR_APP_KEY",
        app_secret="YOUR_APP_SECRET",
    ) as client:
        async with client.ws as ws:
            # Subscribe to Samsung Electronics and SK Hynix
            await ws.subscribe("005930", tr_code="S00")  # 삼성전자
            await ws.subscribe("000660", tr_code="S00")  # SK하이닉스

            print("Monitoring real-time prices... (Ctrl+C to stop)\n")
            print(f"{'Time':<10} {'Code':<10} {'Price':>12} {'Change':>10} {'Volume':>12}")
            print("-" * 56)

            async for msg in ws:
                data = msg.data if isinstance(msg.data, dict) else {}
                stock_code = data.get("tr_key", "")
                price = data.get("price", "")
                change = data.get("change", "")
                volume = data.get("volume", "")
                timestamp = data.get("timestamp", "")
                print(f"{timestamp:<10} {stock_code:<10} {price:>12} {change:>10} {volume:>12}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped.")

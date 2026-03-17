"""Async usage example for pydbsec."""

import asyncio

from pydbsec import AsyncPyDBSec


async def main():
    async with AsyncPyDBSec(
        app_key="YOUR_APP_KEY",
        app_secret="YOUR_APP_SECRET",
    ) as client:
        # Domestic balance
        balance = await client.domestic.balance()
        print(f"예탁총액: {balance.deposit_total:,.0f}원")

        # Stock price
        price = await client.domestic.price("005930")
        print(f"삼성전자: {price.current_price:,.0f}원")

        # Overseas price
        aapl = await client.overseas.price("AAPL", market="FN")
        print(f"AAPL: ${aapl.current_price:.2f}")


if __name__ == "__main__":
    asyncio.run(main())

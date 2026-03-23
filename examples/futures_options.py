"""Futures and options operations.

Demonstrates option tickers, futures price, option board,
and futures balance queries.
"""

from pydbsec import PyDBSec

client = PyDBSec(
    app_key="YOUR_APP_KEY",
    app_secret="YOUR_APP_SECRET",
)

# ── Futures balance ──
print("Futures/Options Balance")
print("=" * 40)
balance = client.futures.balance()
print(f"  예탁총액:   {balance.deposit_total:>12,.0f}원")
print(f"  평가금액:   {balance.eval_amount:>12,.0f}원")
print(f"  평가손익:   {balance.pnl_amount:>12,.0f}원")
print(f"  당일실현:   {balance.realized_pnl:>12,.0f}원")
print(f"  수수료:     {balance.commission:>12,.0f}원")

for pos in balance.positions:
    print(f"  [{pos.stock_code}] {pos.stock_name}: {pos.quantity}계약 | 평가: {pos.eval_amount:,.0f}원")

# ── Option tickers ──
print("\nWeekly Option Tickers (first 5):")
tickers = client.futures.option_tickers(market="WO")
items = tickers.get("Out1", [])[:5]
for item in items:
    print(f"  {item}")

# ── Futures tickers ──
print("\nFutures Tickers (first 5):")
f_tickers = client.futures.future_tickers()
f_items = f_tickers.get("Out1", [])[:5]
for item in f_items:
    print(f"  {item}")

# ── Option price ──
# Use an actual option code from the tickers above
# price = client.futures.price("B09ES887", market="WO")
# print(f"\nOption price: {price}")

# ── Option board ──
print("\nOption Board (월물):")
board = client.futures.option_board(market="OF")
print(f"  Response keys: {list(board.keys())}")

client.close()

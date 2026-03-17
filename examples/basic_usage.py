"""Basic usage example for pydbsec."""

from pydbsec import PyDBSec

# Initialize client
client = PyDBSec(
    app_key="YOUR_APP_KEY",
    app_secret="YOUR_APP_SECRET",
)

# ── Domestic (국내) ──

# Get balance
balance = client.domestic.balance()
print(f"예탁총액: {balance.deposit_total:,.0f}원")
print(f"주문가능: {balance.available_cash:,.0f}원")
print(f"평가손익: {balance.pnl_amount:,.0f}원 ({balance.pnl_rate:+.2f}%)")
for pos in balance.positions:
    print(f"  {pos.stock_name} ({pos.stock_code}): {pos.quantity}주 | 평가: {pos.eval_amount:,.0f}원 | 손익: {pos.pnl_amount:,.0f}원")

# Get stock price
price = client.domestic.price("005930")  # Samsung Electronics
print(f"\n삼성전자 현재가: {price.current_price:,.0f}원 ({price.change_rate:+.2f}%)")
print(f"  거래량: {price.volume:,}")

# Place buy order (limit price)
# result = client.domestic.buy("005930", quantity=10, price=70000)
# print(f"매수 주문번호: {result.order_no}")

# Place sell order (market price)
# result = client.domestic.sell("005930", quantity=5, price_type="03")

# Get chart data
# chart = client.domestic.chart("005930", period="day", start_date="20240101", end_date="20240131")

# ── Overseas (해외) ──

# Get overseas balance
us_balance = client.overseas.balance()
print(f"\n해외 잔고: ${us_balance.eval_total:,.2f}")

# Get overseas stock price
aapl = client.overseas.price("AAPL", market="FN")  # NASDAQ
print(f"AAPL: ${aapl.current_price:.2f} ({aapl.change_rate:+.2f}%)")

# ── Futures (선물) ──

# futures = client.futures.balance()
# print(f"선물 예탁총액: {futures.deposit_total:,.0f}원")

# ── Cleanup ──
client.close()

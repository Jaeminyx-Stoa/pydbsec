"""Complete order lifecycle — check, buy, monitor, cancel.

Demonstrates orderable quantity check, limit order placement,
transaction history monitoring, and order cancellation.
"""

from pydbsec import PyDBSec
from pydbsec.exceptions import InsufficientBalanceError, InvalidOrderError

client = PyDBSec(
    app_key="YOUR_APP_KEY",
    app_secret="YOUR_APP_SECRET",
)

STOCK = "005930"
PRICE = 70000
QTY = 10

# ── 1. Check orderable quantity ──
print("1. Checking orderable quantity...")
available = client.domestic.orderable_quantity(STOCK, price=PRICE)
print(f"   Orderable: {available}")

# ── 2. Place buy order ──
print(f"\n2. Placing buy order: {STOCK} x{QTY} @ {PRICE:,}...")
try:
    result = client.domestic.buy(STOCK, quantity=QTY, price=PRICE)
    print(f"   Order placed: order_no={result.order_no}, success={result.success}")
    order_no = result.order_no
except InsufficientBalanceError as e:
    print(f"   Insufficient balance: {e}")
    client.close()
    raise SystemExit(1)
except InvalidOrderError as e:
    print(f"   Invalid order: {e} (rsp_cd={e.rsp_cd})")
    client.close()
    raise SystemExit(1)

# ── 3. Check transaction history ──
print("\n3. Checking transaction history...")
history = client.domestic.transaction_history(execution_status="0")  # all
print(f"   History response keys: {list(history.keys())}")

# ── 4. Cancel the order ──
print(f"\n4. Cancelling order {order_no}...")
try:
    cancel_result = client.domestic.cancel(order_no=order_no, stock_code=STOCK, quantity=QTY)
    print(f"   Cancelled: order_no={cancel_result.order_no}, success={cancel_result.success}")
except InvalidOrderError as e:
    print(f"   Cancel failed (may already be filled): {e}")

# ── Overseas order example ──
print("\n5. Overseas order example (commented out for safety):")
print("   # result = client.overseas.buy('AAPL', quantity=1, price=180.0)")
print("   # client.overseas.cancel(order_no=result.order_no, stock_code='AAPL', quantity=1)")

client.close()
print("\nDone.")

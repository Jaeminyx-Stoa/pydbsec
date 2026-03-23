"""Comprehensive error handling patterns.

Demonstrates catching each exception type and
retry logic for rate-limited requests.
"""

import time

from pydbsec import PyDBSec
from pydbsec.exceptions import (
    APIError,
    InsufficientBalanceError,
    InvalidOrderError,
    PyDBSecError,
    RateLimitError,
    TokenError,
    ValidationError,
    WebSocketError,
)

client = PyDBSec(
    app_key="YOUR_APP_KEY",
    app_secret="YOUR_APP_SECRET",
)


# ── 1. Validation errors ──
print("1. ValidationError (also a ValueError)")
try:
    client.domestic.price("")  # empty stock code
except ValidationError as e:
    print(f"   Caught ValidationError: {e}")
except ValueError as e:
    # ValidationError is also a ValueError — this also works
    print(f"   Caught ValueError: {e}")


# ── 2. Rate limit with retry ──
def request_with_retry(func, *args, max_retries=3, **kwargs):
    """Retry on rate limit with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except RateLimitError as e:
            wait = e.retry_after or (2 ** attempt)
            print(f"   Rate limited. Retrying in {wait}s... (attempt {attempt + 1}/{max_retries})")
            time.sleep(wait)
    raise RateLimitError("Max retries exceeded")


print("\n2. RateLimitError with retry")
# price = request_with_retry(client.domestic.price, "005930")


# ── 3. Order errors ──
print("\n3. Order error handling")
try:
    # This would raise InvalidOrderError if the order params are bad
    # client.domestic.buy("005930", quantity=10, price=70000)
    pass
except InsufficientBalanceError as e:
    print(f"   Insufficient balance: {e}")
    print(f"   rsp_cd: {e.rsp_cd}")
except InvalidOrderError as e:
    print(f"   Invalid order: {e}")
    print(f"   rsp_cd: {e.rsp_cd}")
except APIError as e:
    # Catches all API errors (parent class)
    print(f"   API error: {e} (HTTP {e.status_code})")


# ── 4. Token errors ──
print("\n4. TokenError handling")
try:
    # Token errors happen during authentication
    # bad_client = PyDBSec(app_key="bad", app_secret="bad")
    pass
except TokenError as e:
    print(f"   Token error: {e} (HTTP {e.status_code})")


# ── 5. WebSocket errors ──
print("\n5. WebSocketError handling")
try:
    # WebSocket errors happen during connection/reconnection
    pass
except WebSocketError as e:
    print(f"   WebSocket error: {e}")


# ── 6. Catch-all ──
print("\n6. PyDBSecError catches everything")
try:
    client.domestic.price("")
except PyDBSecError as e:
    print(f"   Caught: {type(e).__name__}: {e}")


# ── Exception hierarchy ──
print("\n\nException Hierarchy:")
print("  PyDBSecError")
print("  ├── TokenError")
print("  │   └── TokenExpiredError")
print("  ├── APIError")
print("  │   ├── RateLimitError")
print("  │   ├── InvalidOrderError")
print("  │   └── InsufficientBalanceError")
print("  ├── WebSocketError")
print("  └── ValidationError (also ValueError)")

client.close()

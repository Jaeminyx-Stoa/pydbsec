"""Rate limiter for DB Securities API endpoints."""

from __future__ import annotations

import asyncio
import threading
import time

# DB Securities API rate limits (requests per second)
# Source: DB증권 OpenAPI 문서
RATE_LIMITS: dict[str, int] = {
    # Trading — 국내
    "/api/v1/trading/kr-stock/order": 10,
    "/api/v1/trading/kr-stock/order-cancel": 3,
    "/api/v1/trading/kr-stock/inquiry/transaction-history": 2,
    "/api/v1/trading/kr-stock/inquiry/trading-history": 2,
    "/api/v1/trading/kr-stock/inquiry/daliy-trade-report": 2,
    "/api/v1/trading/kr-stock/inquiry/balance": 2,
    "/api/v1/trading/kr-stock/inquiry/able-orderqty": 2,
    "/api/v1/trading/kr-stock/inquiry/acnt-deposit": 1,
    # Trading — 해외
    "/api/v1/trading/overseas-stock/order": 10,
    "/api/v1/trading/overseas-stock/inquiry/transaction-history": 2,
    "/api/v1/trading/overseas-stock/inquiry/balance-margin": 2,
    "/api/v1/trading/overseas-stock/inquiry/deposit-detail": 1,
    "/api/v1/trading/overseas-stock/inquiry/able-orderqty": 2,
    # Trading — 선물
    "/api/v1/trading/kr-futureoption/inquiry/balance": 2,
    # Quote — 국내
    "/api/v1/quote/kr-stock/inquiry/stock-ticker": 2,
    "/api/v1/quote/kr-stock/inquiry/price": 2,
    "/api/v1/quote/kr-stock/inquiry/orderbook": 2,
    # Quote — 해외
    "/api/v1/quote/overseas-stock/inquiry/stock-ticker": 2,
    "/api/v1/quote/overseas-stock/inquiry/price": 2,
    "/api/v1/quote/overseas-stock/inquiry/orderbook": 2,
}

# Default rate limit for endpoints not explicitly listed
DEFAULT_RATE_LIMIT = 2


class RateLimiter:
    """Thread-safe token bucket rate limiter per endpoint."""

    def __init__(self, enabled: bool = True):
        self._enabled = enabled
        self._buckets: dict[str, _TokenBucket] = {}
        self._lock = threading.Lock()

    def wait(self, endpoint: str) -> None:
        """Block until the rate limit allows a request to this endpoint."""
        if not self._enabled:
            return
        bucket = self._get_bucket(endpoint)
        bucket.acquire()

    async def async_wait(self, endpoint: str) -> None:
        """Async version — sleep instead of blocking."""
        if not self._enabled:
            return
        bucket = self._get_bucket(endpoint)
        wait_time = bucket.time_until_available()
        if wait_time > 0:
            await asyncio.sleep(wait_time)
        bucket.acquire()

    def _get_bucket(self, endpoint: str) -> _TokenBucket:
        if endpoint not in self._buckets:
            with self._lock:
                if endpoint not in self._buckets:
                    rps = RATE_LIMITS.get(endpoint, DEFAULT_RATE_LIMIT)
                    self._buckets[endpoint] = _TokenBucket(rps)
        return self._buckets[endpoint]


class _TokenBucket:
    """Simple token bucket for rate limiting."""

    def __init__(self, rate: int):
        self._rate = rate  # tokens per second
        self._tokens = float(rate)
        self._last_refill = time.monotonic()
        self._lock = threading.Lock()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self._rate, self._tokens + elapsed * self._rate)
        self._last_refill = now

    def acquire(self) -> None:
        with self._lock:
            self._refill()
            if self._tokens < 1:
                wait = (1 - self._tokens) / self._rate
                time.sleep(wait)
                self._refill()
            self._tokens -= 1

    def time_until_available(self) -> float:
        with self._lock:
            self._refill()
            if self._tokens >= 1:
                return 0.0
            return (1 - self._tokens) / self._rate

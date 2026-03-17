"""Tests for rate limiter."""

import time

from pydbsec.ratelimit import RateLimiter, _TokenBucket


class TestTokenBucket:
    def test_allows_burst_up_to_rate(self):
        bucket = _TokenBucket(rate=5)
        # Should allow 5 immediate acquires
        for _ in range(5):
            bucket.acquire()

    def test_throttles_after_burst(self):
        bucket = _TokenBucket(rate=10)
        # Drain all tokens
        for _ in range(10):
            bucket.acquire()
        # Next acquire should take ~0.1s (1/10)
        start = time.monotonic()
        bucket.acquire()
        elapsed = time.monotonic() - start
        assert elapsed >= 0.05  # at least 50ms wait

    def test_time_until_available(self):
        bucket = _TokenBucket(rate=2)
        bucket.acquire()
        bucket.acquire()
        wait = bucket.time_until_available()
        assert wait > 0


class TestRateLimiter:
    def test_disabled(self):
        rl = RateLimiter(enabled=False)
        # Should not block at all
        start = time.monotonic()
        for _ in range(100):
            rl.wait("/api/v1/test")
        elapsed = time.monotonic() - start
        assert elapsed < 0.1  # basically instant

    def test_enabled_respects_limits(self):
        rl = RateLimiter(enabled=True)
        endpoint = "/api/v1/trading/kr-stock/order"  # 10 rps
        # 10 requests should be instant (burst)
        start = time.monotonic()
        for _ in range(10):
            rl.wait(endpoint)
        elapsed = time.monotonic() - start
        assert elapsed < 0.5

    def test_unknown_endpoint_uses_default(self):
        rl = RateLimiter(enabled=True)
        # Unknown endpoint gets default rate (2 rps)
        rl.wait("/api/v1/unknown/endpoint")
        rl.wait("/api/v1/unknown/endpoint")
        # Third should be slightly delayed
        start = time.monotonic()
        rl.wait("/api/v1/unknown/endpoint")
        elapsed = time.monotonic() - start
        assert elapsed >= 0.1  # waited for token refill


class TestClientRateLimit:
    def test_rate_limit_enabled_by_default(self, httpx_mock):
        """PyDBSec should have rate limiting enabled by default."""
        from datetime import datetime, timedelta

        from pydbsec import PyDBSec

        client = PyDBSec(
            "key",
            "secret",
            token="tok",
            token_type="Bearer",
            expires_at=datetime.now() + timedelta(hours=1),
        )
        assert client._http._rate_limiter is not None
        assert client._http._rate_limiter._enabled is True

    def test_rate_limit_disabled(self, httpx_mock):
        from datetime import datetime, timedelta

        from pydbsec import PyDBSec

        client = PyDBSec(
            "key",
            "secret",
            token="tok",
            token_type="Bearer",
            expires_at=datetime.now() + timedelta(hours=1),
            rate_limit=False,
        )
        assert client._http._rate_limiter._enabled is False

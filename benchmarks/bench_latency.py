"""Benchmark: HTTP client latency and rate limiter overhead.

Run with real credentials:
    DBSEC_APP_KEY=xxx DBSEC_APP_SECRET=yyy python benchmarks/bench_latency.py

Measures:
- Single request latency (avg, p50, p95, p99)
- Rate limiter overhead
- Connection pool reuse vs fresh connection
"""

import os
import statistics
import sys
import time


def _require_creds():
    if not os.environ.get("DBSEC_APP_KEY"):
        print("DBSEC_APP_KEY not set. Set credentials to run benchmarks.")
        sys.exit(1)


def bench_single_request(n: int = 20):
    """Benchmark single price() request latency."""
    from pydbsec import PyDBSec

    client = PyDBSec(
        app_key=os.environ["DBSEC_APP_KEY"],
        app_secret=os.environ["DBSEC_APP_SECRET"],
        rate_limit=False,
    )

    # Warmup
    client.domestic.price("005930")

    latencies = []
    for _ in range(n):
        start = time.perf_counter()
        client.domestic.price("005930")
        elapsed = (time.perf_counter() - start) * 1000  # ms
        latencies.append(elapsed)

    client.close()

    latencies.sort()
    print(f"\n{'Single Request Latency':=^50}")
    print(f"  Requests: {n}")
    print(f"  Avg:  {statistics.mean(latencies):.1f} ms")
    print(f"  P50:  {latencies[len(latencies) // 2]:.1f} ms")
    print(f"  P95:  {latencies[int(len(latencies) * 0.95)]:.1f} ms")
    print(f"  P99:  {latencies[int(len(latencies) * 0.99)]:.1f} ms")
    print(f"  Min:  {min(latencies):.1f} ms")
    print(f"  Max:  {max(latencies):.1f} ms")


def bench_rate_limiter_overhead(n: int = 100):
    """Benchmark rate limiter wait() overhead (no actual HTTP)."""
    from pydbsec.ratelimit import RateLimiter

    limiter = RateLimiter(enabled=True)
    endpoint = "/api/v1/quote/kr-stock/inquiry/price"

    latencies = []
    for _ in range(n):
        start = time.perf_counter()
        limiter.wait(endpoint)
        elapsed = (time.perf_counter() - start) * 1_000_000  # µs
        latencies.append(elapsed)

    print(f"\n{'Rate Limiter Overhead':=^50}")
    print(f"  Calls: {n}")
    print(f"  Avg:  {statistics.mean(latencies):.1f} µs")
    print(f"  Max:  {max(latencies):.1f} µs")


def bench_model_parsing(n: int = 1000):
    """Benchmark Pydantic model parsing throughput."""
    from pydbsec.models.quote import ChartCandle, ChartData

    sample_data = {
        "Out": {},
        "Out1": [
            {"TrdDd": f"2026032{i % 10}", "Oprc": "71000", "Hprc": "72500", "Lprc": "70500", "Clpr": "72000", "AcmlVol": "15000000"}
            for i in range(50)
        ],
    }

    start = time.perf_counter()
    for _ in range(n):
        ChartData.from_api(sample_data)
    elapsed = time.perf_counter() - start

    print(f"\n{'Model Parsing Throughput':=^50}")
    print(f"  Iterations: {n} (50 candles each)")
    print(f"  Total:  {elapsed * 1000:.1f} ms")
    print(f"  Per parse: {elapsed / n * 1000:.2f} ms")
    print(f"  Throughput: {n / elapsed:,.0f} parses/sec")


if __name__ == "__main__":
    print("pydbsec Benchmarks")
    print("=" * 50)

    # Local benchmarks (no API needed)
    bench_rate_limiter_overhead()
    bench_model_parsing()

    # Remote benchmarks (requires credentials)
    if os.environ.get("DBSEC_APP_KEY"):
        bench_single_request()
    else:
        print("\n(Skipping remote benchmarks — set DBSEC_APP_KEY)")

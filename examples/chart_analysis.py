"""Chart data retrieval and simple moving average calculation.

Demonstrates the ChartData model — typed candle access,
SMA computation, and different chart periods.
"""

from pydbsec import PyDBSec

client = PyDBSec(
    app_key="YOUR_APP_KEY",
    app_secret="YOUR_APP_SECRET",
)

# ── Daily chart ──
chart = client.domestic.chart(
    "005930",
    period="day",
    start_date="20260301",
    end_date="20260320",
)

print(f"Samsung Electronics — {len(chart.candles)} candles\n")
print(f"{'Date':<12} {'Open':>10} {'High':>10} {'Low':>10} {'Close':>10} {'Volume':>14}")
print("-" * 70)
for c in chart.candles:
    print(f"{c.date:<12} {c.open:>10,.0f} {c.high:>10,.0f} {c.low:>10,.0f} {c.close:>10,.0f} {c.volume:>14,}")

# ── Simple Moving Average ──
if len(chart.candles) >= 5:
    closes = [c.close for c in chart.candles[:5]]
    sma5 = sum(closes) / 5
    print(f"\n5-day SMA: {sma5:,.0f}")

# ── Minute chart ──
minute_chart = client.domestic.chart(
    "005930",
    period="minute",
    time_interval="300",  # 5-minute candles
)
print(f"\nMinute chart: {len(minute_chart.candles)} candles")
for c in minute_chart.candles[:5]:
    print(f"  {c.date} {c.time} | Close: {c.close:,.0f} | Vol: {c.volume:,}")

# ── Overseas chart ──
aapl = client.overseas.chart("AAPL", period="day", start_date="20260301", end_date="20260320")
print(f"\nAAPL — {len(aapl.candles)} candles")
for c in aapl.candles[:3]:
    print(f"  {c.date} | O:{c.open:.2f} H:{c.high:.2f} L:{c.low:.2f} C:{c.close:.2f}")

# ── Raw data access ──
# The original API dict is always available via .raw
print(f"\nRaw keys: {list(chart.raw.keys())}")

client.close()

"""Unified portfolio summary — domestic + overseas in one view."""

from pydbsec import PyDBSec

client = PyDBSec(
    app_key="YOUR_APP_KEY",
    app_secret="YOUR_APP_SECRET",
)

# ── Unified portfolio ──
summary = client.portfolio_summary(include_overseas=True)

print("=" * 60)
print("Portfolio Summary")
print("=" * 60)

# Domestic
kr = summary.get("domestic", {})
print(f"\n[국내]")
print(f"  예탁총액: {kr.get('deposit_total', 0):>15,.0f}원")
print(f"  평가총액: {kr.get('eval_total', 0):>15,.0f}원")
print(f"  평가손익: {kr.get('pnl_amount', 0):>15,.0f}원 ({kr.get('pnl_rate', 0):+.2f}%)")

for pos in kr.get("positions", []):
    print(f"    {pos['stock_name']:<12} {pos['quantity']:>6}주  평가: {pos['eval_amount']:>12,.0f}원  손익: {pos['pnl_amount']:>10,.0f}원")

# Overseas
us = summary.get("overseas", {})
print(f"\n[해외]")
print(f"  평가총액: ${us.get('eval_total', 0):>14,.2f}")
print(f"  평가손익: ${us.get('pnl_amount', 0):>14,.2f} ({us.get('pnl_rate', 0):+.2f}%)")

for pos in us.get("positions", []):
    print(f"    {pos['stock_name']:<12} {pos['quantity']:>6}주  평가: ${pos['eval_amount']:>11,.2f}  손익: ${pos['pnl_amount']:>9,.2f}")

print(f"\n{'=' * 60}")

client.close()

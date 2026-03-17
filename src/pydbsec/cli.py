"""CLI tool for pydbsec — query DB Securities API from the terminal.

Usage::

    # Set credentials (one-time)
    export DBSEC_APP_KEY="your_app_key"
    export DBSEC_APP_SECRET="your_app_secret"

    # Commands
    pydbsec price 005930              # 삼성전자 현재가
    pydbsec price AAPL --market FN    # NASDAQ AAPL
    pydbsec balance                   # 국내 잔고
    pydbsec balance --overseas        # 해외 잔고
    pydbsec portfolio                 # 국내+해외 통합
    pydbsec buy 005930 10 70000       # 삼성전자 10주 70000원 매수
    pydbsec sell 005930 5 72000       # 삼성전자 5주 72000원 매도
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="pydbsec",
        description="DB Securities (DB증권) OpenAPI CLI",
    )
    parser.add_argument("--key", default=os.environ.get("DBSEC_APP_KEY"), help="App key (or set DBSEC_APP_KEY)")
    parser.add_argument(
        "--secret", default=os.environ.get("DBSEC_APP_SECRET"), help="App secret (or set DBSEC_APP_SECRET)"
    )
    parser.add_argument("--json", action="store_true", dest="as_json", help="Output raw JSON")

    sub = parser.add_subparsers(dest="command", help="Available commands")

    # price
    p_price = sub.add_parser("price", help="Get current stock price")
    p_price.add_argument("stock_code", help="Stock code (e.g., 005930, AAPL)")
    p_price.add_argument("--market", default=None, help="Market code (UJ, FY, FN, FA)")
    p_price.add_argument("--overseas", action="store_true", help="Query overseas market")

    # balance
    p_bal = sub.add_parser("balance", help="Get account balance")
    p_bal.add_argument("--overseas", action="store_true", help="Get overseas balance")

    # portfolio
    sub.add_parser("portfolio", help="Get unified portfolio summary (KR+US)")

    # buy
    p_buy = sub.add_parser("buy", help="Place a buy order")
    p_buy.add_argument("stock_code", help="Stock code")
    p_buy.add_argument("quantity", type=int, help="Number of shares")
    p_buy.add_argument("price", type=float, help="Order price")
    p_buy.add_argument("--overseas", action="store_true", help="Overseas order")

    # sell
    p_sell = sub.add_parser("sell", help="Place a sell order")
    p_sell.add_argument("stock_code", help="Stock code")
    p_sell.add_argument("quantity", type=int, help="Number of shares")
    p_sell.add_argument("price", type=float, help="Order price")
    p_sell.add_argument("--overseas", action="store_true", help="Overseas order")

    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    if not args.key or not args.secret:
        print("Error: App key and secret required.", file=sys.stderr)
        print("Set DBSEC_APP_KEY and DBSEC_APP_SECRET environment variables,", file=sys.stderr)
        print("or use --key and --secret flags.", file=sys.stderr)
        return 1

    from .client import PyDBSec

    try:
        client = PyDBSec(app_key=args.key, app_secret=args.secret)
    except Exception as e:
        print(f"Error: Failed to connect — {e}", file=sys.stderr)
        return 1

    try:
        if args.command == "price":
            _cmd_price(client, args)
        elif args.command == "balance":
            _cmd_balance(client, args)
        elif args.command == "portfolio":
            _cmd_portfolio(client, args)
        elif args.command == "buy":
            _cmd_buy(client, args)
        elif args.command == "sell":
            _cmd_sell(client, args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    finally:
        client._http.close()

    return 0


def _cmd_price(client: Any, args: argparse.Namespace) -> None:
    if args.overseas:
        market = args.market or "FY"
        price = client.overseas.price(args.stock_code, market=market)
    else:
        market = args.market or "UJ"
        price = client.domestic.price(args.stock_code, market=market)

    if args.as_json:
        print(json.dumps(price.raw, ensure_ascii=False, indent=2))
    else:
        sign = "+" if price.change >= 0 else ""
        print(f"{args.stock_code}")
        print(f"  Price:  {price.current_price:,.2f}")
        print(f"  Change: {sign}{price.change:,.2f} ({sign}{price.change_rate:.2f}%)")
        print(f"  Volume: {price.volume:,}")
        print(f"  High:   {price.high_price:,.2f}  Low: {price.low_price:,.2f}  Open: {price.open_price:,.2f}")


def _cmd_balance(client: Any, args: argparse.Namespace) -> None:
    if args.overseas:
        bal = client.overseas.balance()
        if args.as_json:
            print(json.dumps(bal.raw, ensure_ascii=False, indent=2))
            return
        print("Overseas Balance")
        print(f"  Total:     ${bal.deposit_total:,.2f}")
        print(f"  Cash:      ${bal.available_cash:,.2f}")
        print(f"  P&L:       ${bal.pnl_amount:,.2f} ({bal.pnl_rate:+.2f}%)")
        if bal.positions:
            print("  Positions:")
            for p in bal.positions:
                print(
                    f"    {p.stock_code:8s} {p.stock_name:16s} {p.quantity:>5d}"
                    f"  ${p.eval_amount:>10,.2f}  P&L: ${p.pnl_amount:>10,.2f}"
                )
    else:
        bal = client.domestic.balance()
        if args.as_json:
            print(json.dumps(bal.raw, ensure_ascii=False, indent=2))
            return
        print("Domestic Balance")
        print(f"  Total:     {bal.deposit_total:>15,.0f} KRW")
        print(f"  Cash:      {bal.available_cash:>15,.0f} KRW")
        print(f"  P&L:       {bal.pnl_amount:>15,.0f} KRW ({bal.pnl_rate:+.2f}%)")
        if bal.positions:
            print("  Positions:")
            for p in bal.positions:
                print(
                    f"    {p.stock_code:8s} {p.stock_name:16s} {p.quantity:>5d}"
                    f"  {p.eval_amount:>12,.0f}  P&L: {p.pnl_amount:>10,.0f}"
                )


def _cmd_portfolio(client: Any, args: argparse.Namespace) -> None:
    summary = client.portfolio_summary()
    if args.as_json:
        print(json.dumps(summary, ensure_ascii=False, indent=2, default=str))
        return
    print("Portfolio Summary")
    print(f"  Total NAV: {summary['total_nav']:>15,.0f}")
    print(f"  Cash:      {summary['cash']:>15,.0f}")
    print(f"  Profit:    {summary['profit']:>15,.0f} ({summary['ror']:+.2f}%)")
    if summary.get("overseas_nav"):
        print(f"  Overseas:  {summary['overseas_nav']:>15,.0f}")
    if summary["positions"]:
        print(f"  Positions ({len(summary['positions'])}):")
        for p in summary["positions"]:
            print(
                f"    [{p['region']}] {p['stock_code']:8s} {p['stock_name']:16s}"
                f" {p['quantity']:>5d}  P&L: {p['pnl_amount']:>10,.0f}"
            )


def _cmd_buy(client: Any, args: argparse.Namespace) -> None:
    if args.overseas:
        result = client.overseas.buy(args.stock_code, args.quantity, args.price)
    else:
        result = client.domestic.buy(args.stock_code, args.quantity, args.price)

    if args.as_json:
        print(json.dumps(result.raw, ensure_ascii=False, indent=2))
    else:
        status = "OK" if result.success else "FAILED"
        print(f"BUY {args.stock_code} x{args.quantity} @ {args.price:,.2f} — {status}")
        if result.order_no:
            print(f"  Order#: {result.order_no}")
        if result.message:
            print(f"  Message: {result.message}")


def _cmd_sell(client: Any, args: argparse.Namespace) -> None:
    if args.overseas:
        result = client.overseas.sell(args.stock_code, args.quantity, args.price)
    else:
        result = client.domestic.sell(args.stock_code, args.quantity, args.price)

    if args.as_json:
        print(json.dumps(result.raw, ensure_ascii=False, indent=2))
    else:
        status = "OK" if result.success else "FAILED"
        print(f"SELL {args.stock_code} x{args.quantity} @ {args.price:,.2f} — {status}")
        if result.order_no:
            print(f"  Order#: {result.order_no}")
        if result.message:
            print(f"  Message: {result.message}")


if __name__ == "__main__":
    sys.exit(main())

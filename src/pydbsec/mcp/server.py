"""MCP server exposing DB Securities API as tools for AI assistants.

Usage:
    # Run directly
    pydbsec-mcp

    # Claude Desktop config (claude_desktop_config.json)
    {
        "mcpServers": {
            "dbsec": {
                "command": "pydbsec-mcp",
                "env": {
                    "DBSEC_APP_KEY": "your_app_key",
                    "DBSEC_APP_SECRET": "your_app_secret"
                }
            }
        }
    }
"""

from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING, Any

from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    from pydbsec import PyDBSec

mcp = FastMCP(
    "DB Securities",
    instructions=(
        "DB증권 OpenAPI를 통해 한국/미국 주식 시세 조회, 잔고 확인, 매수/매도 주문을 수행할 수 있습니다. "
        "환경변수 DBSEC_APP_KEY와 DBSEC_APP_SECRET이 설정되어 있어야 합니다."
    ),
)


def _get_client() -> PyDBSec:
    """Lazy-initialize PyDBSec client from env vars."""
    from pydbsec import PyDBSec

    app_key = os.environ.get("DBSEC_APP_KEY", "")
    app_secret = os.environ.get("DBSEC_APP_SECRET", "")
    if not app_key or not app_secret:
        raise ValueError(
            "DBSEC_APP_KEY and DBSEC_APP_SECRET environment variables are required. "
            "Get them from https://openapi.dbsec.co.kr"
        )
    return PyDBSec(app_key=app_key, app_secret=app_secret)


# ── Stock Price ──


@mcp.tool()
def get_stock_price(stock_code: str, overseas: bool = False, market: str = "") -> str:
    """주식 현재가를 조회합니다.

    Args:
        stock_code: 종목코드 (국내: "005930", 해외: "AAPL")
        overseas: True이면 해외 주식 조회
        market: 시장코드 (국내: UJ/E/EN, 해외: FY=NYSE/FN=NASDAQ/FA=AMEX). 비어있으면 기본값 사용.
    """
    client = _get_client()
    try:
        if overseas:
            mkt = market or "FY"
            price = client.overseas.price(stock_code, market=mkt)
        else:
            mkt = market or "UJ"
            price = client.domestic.price(stock_code, market=mkt)

        return json.dumps(
            {
                "stock_code": stock_code,
                "current_price": price.current_price,
                "change": price.change,
                "change_rate": price.change_rate,
                "volume": price.volume,
                "high": price.high_price,
                "low": price.low_price,
                "open": price.open_price,
            },
            ensure_ascii=False,
        )
    finally:
        client._http.close()


# ── Balance ──


@mcp.tool()
def get_balance(overseas: bool = False) -> str:
    """주식 잔고를 조회합니다.

    Args:
        overseas: True이면 해외 잔고, False이면 국내 잔고
    """
    client = _get_client()
    try:
        pos_list: list[Any]
        if overseas:
            us_bal = client.overseas.balance()
            deposit, cash, pnl, rate = us_bal.deposit_total, us_bal.available_cash, us_bal.pnl_amount, us_bal.pnl_rate
            pos_list = us_bal.positions
        else:
            kr_bal = client.domestic.balance()
            deposit, cash, pnl, rate = kr_bal.deposit_total, kr_bal.available_cash, kr_bal.pnl_amount, kr_bal.pnl_rate
            pos_list = kr_bal.positions

        positions = [
            {
                "stock_code": p.stock_code,
                "stock_name": p.stock_name,
                "quantity": p.quantity,
                "current_price": p.current_price,
                "eval_amount": p.eval_amount,
                "pnl_amount": p.pnl_amount,
                "pnl_rate": p.pnl_rate,
            }
            for p in pos_list
        ]

        return json.dumps(
            {
                "deposit_total": deposit,
                "available_cash": cash,
                "pnl_amount": pnl,
                "pnl_rate": rate,
                "positions": positions,
            },
            ensure_ascii=False,
        )
    finally:
        client._http.close()


# ── Portfolio Summary ──


@mcp.tool()
def get_portfolio_summary(include_overseas: bool = True) -> str:
    """국내+해외 통합 포트폴리오 요약을 조회합니다.

    Args:
        include_overseas: True이면 해외 잔고도 포함 (기본값: True)
    """
    client = _get_client()
    try:
        summary = client.portfolio_summary(include_overseas=include_overseas)
        return json.dumps(summary, ensure_ascii=False, default=str)
    finally:
        client._http.close()


# ── Order ──


@mcp.tool()
def place_order(
    stock_code: str,
    side: str,
    quantity: int,
    price: float,
    overseas: bool = False,
) -> str:
    """주식 매수/매도 주문을 실행합니다. 실제 주문이 실행되므로 주의하세요.

    Args:
        stock_code: 종목코드 (국내: "005930", 해외: "AAPL")
        side: "buy" 또는 "sell"
        quantity: 주문 수량
        price: 주문 가격
        overseas: True이면 해외 주식 주문
    """
    client = _get_client()
    try:
        if side == "buy":
            if overseas:
                result = client.overseas.buy(stock_code, quantity, price)
            else:
                result = client.domestic.buy(stock_code, quantity, price)
        elif side == "sell":
            if overseas:
                result = client.overseas.sell(stock_code, quantity, price)
            else:
                result = client.domestic.sell(stock_code, quantity, price)
        else:
            return json.dumps({"error": f"Invalid side: {side}. Must be 'buy' or 'sell'."})

        return json.dumps(
            {
                "success": result.success,
                "order_no": result.order_no,
                "message": result.message,
            },
            ensure_ascii=False,
        )
    finally:
        client._http.close()


# ── Order Book ──


@mcp.tool()
def get_order_book(stock_code: str, overseas: bool = False, market: str = "") -> str:
    """호가(매수/매도 호가창)를 조회합니다.

    Args:
        stock_code: 종목코드
        overseas: True이면 해외 주식
        market: 시장코드 (비어있으면 기본값)
    """
    client = _get_client()
    try:
        if overseas:
            mkt = market or "FY"
            ob = client.overseas.order_book(stock_code, market=mkt)
        else:
            mkt = market or "UJ"
            ob = client.domestic.order_book(stock_code, market=mkt)
        return json.dumps(ob.raw, ensure_ascii=False)
    finally:
        client._http.close()


# ── Chart ──


@mcp.tool()
def get_chart(
    stock_code: str,
    period: str = "day",
    start_date: str = "",
    end_date: str = "",
    overseas: bool = False,
    market: str = "",
) -> str:
    """주식 차트 데이터를 조회합니다.

    Args:
        stock_code: 종목코드
        period: "minute", "day", "week", "month"
        start_date: 시작일 (YYYYMMDD)
        end_date: 종료일 (YYYYMMDD)
        overseas: True이면 해외 주식
        market: 시장코드 (비어있으면 기본값)
    """
    client = _get_client()
    try:
        if overseas:
            mkt = market or "FY"
            data = client.overseas.chart(
                stock_code, period=period, start_date=start_date, end_date=end_date, market=mkt
            )
        else:
            mkt = market or "UJ"
            data = client.domestic.chart(
                stock_code, period=period, start_date=start_date, end_date=end_date, market=mkt
            )
        return json.dumps(data.raw, ensure_ascii=False)
    finally:
        client._http.close()


def run_server() -> None:
    """Entry point for pydbsec-mcp command."""
    mcp.run(transport="stdio")

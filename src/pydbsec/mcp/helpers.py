"""MCP helper utilities for pydbsec.

1. Anthropic SDK integration — use pydbsec MCP tools with anthropic tool runner
2. Client helpers — easily connect to pydbsec MCP server from any app
3. Response parsing — convert MCP tool results to pydbsec Pydantic models
"""

from __future__ import annotations

import json
from typing import Any

from ..models.balance import DomesticBalance, DomesticPosition, OverseasBalance, OverseasPosition
from ..models.order import OrderResult
from ..models.quote import OrderBook, StockPrice

# ══════════════════════════════════════════════════════════════════════
# 1. Anthropic SDK Integration
# ══════════════════════════════════════════════════════════════════════


def get_anthropic_tools() -> list[dict[str, Any]]:
    """Get pydbsec tools as Anthropic API tool definitions.

    Use with `client.messages.create(tools=get_anthropic_tools())`.

    Returns:
        List of tool definitions compatible with Anthropic Messages API.

    Example::

        import anthropic
        from pydbsec.mcp.helpers import get_anthropic_tools

        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=4096,
            tools=get_anthropic_tools(),
            messages=[{"role": "user", "content": "삼성전자 현재가 알려줘"}],
        )
    """
    return [
        {
            "name": "get_stock_price",
            "description": "주식 현재가를 조회합니다. 국내(005930) 또는 해외(AAPL) 주식 시세를 조회합니다.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "stock_code": {"type": "string", "description": "종목코드 (국내: '005930', 해외: 'AAPL')"},
                    "overseas": {"type": "boolean", "description": "True이면 해외 주식 조회", "default": False},
                    "market": {"type": "string", "description": "시장코드 (국내: UJ, 해외: FY/FN/FA)", "default": ""},
                },
                "required": ["stock_code"],
            },
        },
        {
            "name": "get_balance",
            "description": "주식 잔고를 조회합니다. 국내 또는 해외 잔고를 확인합니다.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "overseas": {"type": "boolean", "description": "True이면 해외 잔고", "default": False},
                },
                "required": [],
            },
        },
        {
            "name": "get_portfolio_summary",
            "description": "국내+해외 통합 포트폴리오 요약을 조회합니다.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "include_overseas": {"type": "boolean", "description": "해외 포함 여부", "default": True},
                },
                "required": [],
            },
        },
        {
            "name": "place_order",
            "description": "주식 매수/매도 주문을 실행합니다. 실제 주문이므로 주의.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "stock_code": {"type": "string", "description": "종목코드"},
                    "side": {"type": "string", "enum": ["buy", "sell"], "description": "매수/매도"},
                    "quantity": {"type": "integer", "description": "주문 수량"},
                    "price": {"type": "number", "description": "주문 가격"},
                    "overseas": {"type": "boolean", "description": "해외 주문 여부", "default": False},
                },
                "required": ["stock_code", "side", "quantity", "price"],
            },
        },
        {
            "name": "get_order_book",
            "description": "호가(매수/매도 호가창)를 조회합니다.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "stock_code": {"type": "string", "description": "종목코드"},
                    "overseas": {"type": "boolean", "default": False},
                    "market": {"type": "string", "default": ""},
                },
                "required": ["stock_code"],
            },
        },
        {
            "name": "get_chart",
            "description": "주식 차트 데이터를 조회합니다.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "stock_code": {"type": "string", "description": "종목코드"},
                    "period": {"type": "string", "enum": ["minute", "day", "week", "month"], "default": "day"},
                    "start_date": {"type": "string", "description": "YYYYMMDD", "default": ""},
                    "end_date": {"type": "string", "description": "YYYYMMDD", "default": ""},
                    "overseas": {"type": "boolean", "default": False},
                    "market": {"type": "string", "default": ""},
                },
                "required": ["stock_code"],
            },
        },
    ]


def execute_tool(tool_name: str, tool_input: dict[str, Any]) -> str:
    """Execute a pydbsec MCP tool locally (without MCP transport).

    Use this as the tool executor in an Anthropic API agentic loop.

    Args:
        tool_name: Tool name from Claude's tool_use block
        tool_input: Tool input from Claude's tool_use block

    Returns:
        JSON string result (same format as MCP server)
    """
    from .server import get_balance, get_chart, get_order_book, get_portfolio_summary, get_stock_price, place_order

    executors: dict[str, Any] = {
        "get_stock_price": get_stock_price,
        "get_balance": get_balance,
        "get_portfolio_summary": get_portfolio_summary,
        "place_order": place_order,
        "get_order_book": get_order_book,
        "get_chart": get_chart,
    }

    executor = executors.get(tool_name)
    if executor is None:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})

    try:
        result: str = executor(**tool_input)
        return result
    except Exception as e:
        return json.dumps({"error": str(e)})


# ══════════════════════════════════════════════════════════════════════
# 2. MCP Client Helpers
# ══════════════════════════════════════════════════════════════════════


class DBSecMCPClient:
    """Helper to connect to pydbsec MCP server from any application.

    Example::

        from pydbsec.mcp.helpers import DBSecMCPClient

        async with DBSecMCPClient(app_key="...", app_secret="...") as client:
            price = await client.get_stock_price("005930")
            print(price.current_price)

            balance = await client.get_balance()
            print(balance.deposit_total)
    """

    def __init__(
        self,
        app_key: str,
        app_secret: str,
        *,
        command: str = "pydbsec-mcp",
    ):
        self._app_key = app_key
        self._app_secret = app_secret
        self._command = command
        self._session: Any = None
        self._read: Any = None
        self._write: Any = None
        self._cm: Any = None

    async def connect(self) -> None:
        """Connect to the pydbsec MCP server."""
        from mcp import ClientSession
        from mcp.client.stdio import StdioServerParameters, stdio_client

        params = StdioServerParameters(
            command=self._command,
            env={"DBSEC_APP_KEY": self._app_key, "DBSEC_APP_SECRET": self._app_secret},
        )
        self._cm = stdio_client(params)
        self._read, self._write = await self._cm.__aenter__()
        self._session = ClientSession(self._read, self._write)
        await self._session.__aenter__()
        await self._session.initialize()

    async def disconnect(self) -> None:
        """Disconnect from the MCP server."""
        if self._session:
            await self._session.__aexit__(None, None, None)
        if self._cm:
            await self._cm.__aexit__(None, None, None)

    async def call(self, tool_name: str, **kwargs: Any) -> dict[str, Any]:
        """Call an MCP tool and return parsed JSON result."""
        if not self._session:
            raise RuntimeError("Not connected. Call connect() first.")
        result = await self._session.call_tool(tool_name, kwargs)
        text = result.content[0].text if result.content else "{}"
        return json.loads(text)  # type: ignore[no-any-return]

    async def get_stock_price(self, stock_code: str, *, overseas: bool = False, market: str = "") -> StockPrice:
        """Get stock price as a typed StockPrice model."""
        data = await self.call("get_stock_price", stock_code=stock_code, overseas=overseas, market=market)
        return parse_stock_price(data)

    async def get_balance(self, *, overseas: bool = False) -> DomesticBalance | OverseasBalance:
        """Get balance as a typed model."""
        data = await self.call("get_balance", overseas=overseas)
        return parse_balance(data, overseas=overseas)

    async def get_portfolio_summary(self, *, include_overseas: bool = True) -> dict[str, Any]:
        """Get portfolio summary."""
        return await self.call("get_portfolio_summary", include_overseas=include_overseas)

    async def place_order(
        self, stock_code: str, side: str, quantity: int, price: float, *, overseas: bool = False
    ) -> OrderResult:
        """Place an order and return typed result."""
        data = await self.call(
            "place_order", stock_code=stock_code, side=side, quantity=quantity, price=price, overseas=overseas
        )
        return parse_order_result(data)

    async def __aenter__(self) -> DBSecMCPClient:
        await self.connect()
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.disconnect()


# ══════════════════════════════════════════════════════════════════════
# 3. Response Parsing — MCP result JSON → pydbsec Pydantic models
# ══════════════════════════════════════════════════════════════════════


def _ensure_dict(data: dict[str, Any] | str) -> dict[str, Any]:
    """Convert str to dict if needed."""
    if isinstance(data, str):
        return json.loads(data)  # type: ignore[no-any-return]
    return data


def parse_stock_price(data: dict[str, Any] | str) -> StockPrice:
    """Parse MCP tool result into a StockPrice model.

    Args:
        data: Dict from parsed JSON, or raw JSON string

    Example::

        result = await session.call_tool("get_stock_price", {"stock_code": "005930"})
        price = parse_stock_price(json.loads(result.content[0].text))
        print(price.current_price)
    """
    d = _ensure_dict(data)
    return StockPrice(
        current_price=d.get("current_price", 0),
        change=d.get("change", 0),
        change_rate=d.get("change_rate", 0),
        volume=d.get("volume", 0),
        open_price=d.get("open", 0),
        high_price=d.get("high", 0),
        low_price=d.get("low", 0),
        raw=d,
    )


def parse_balance(data: dict[str, Any] | str, *, overseas: bool = False) -> DomesticBalance | OverseasBalance:
    """Parse MCP tool result into a Balance model."""
    d = _ensure_dict(data)
    positions_data = d.get("positions", [])

    if overseas:
        positions_us = [
            OverseasPosition(
                stock_code=p.get("stock_code", ""),
                stock_name=p.get("stock_name", ""),
                quantity=p.get("quantity", 0),
                current_price=p.get("current_price", 0),
                eval_amount=p.get("eval_amount", 0),
                pnl_amount=p.get("pnl_amount", 0),
                pnl_rate=p.get("pnl_rate", 0),
            )
            for p in positions_data
        ]
        return OverseasBalance(
            deposit_total=d.get("deposit_total", 0),
            available_cash=d.get("available_cash", 0),
            pnl_amount=d.get("pnl_amount", 0),
            pnl_rate=d.get("pnl_rate", 0),
            positions=positions_us,
            raw=d,
        )
    else:
        positions_kr = [
            DomesticPosition(
                stock_code=p.get("stock_code", ""),
                stock_name=p.get("stock_name", ""),
                quantity=p.get("quantity", 0),
                current_price=p.get("current_price", 0),
                eval_amount=p.get("eval_amount", 0),
                pnl_amount=p.get("pnl_amount", 0),
                pnl_rate=p.get("pnl_rate", 0),
            )
            for p in positions_data
        ]
        return DomesticBalance(
            deposit_total=d.get("deposit_total", 0),
            available_cash=d.get("available_cash", 0),
            pnl_amount=d.get("pnl_amount", 0),
            pnl_rate=d.get("pnl_rate", 0),
            positions=positions_kr,
            raw=d,
        )


def parse_order_result(data: dict[str, Any] | str) -> OrderResult:
    """Parse MCP tool result into an OrderResult model."""
    d = _ensure_dict(data)
    return OrderResult(
        success=d.get("success", False),
        order_no=d.get("order_no", 0),
        message=d.get("message", ""),
        raw=d,
    )


def parse_order_book(data: dict[str, Any] | str) -> OrderBook:
    """Parse MCP tool result into an OrderBook model."""
    d = _ensure_dict(data)
    return OrderBook.from_api(d)

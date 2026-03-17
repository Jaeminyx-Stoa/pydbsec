"""Tests for MCP helpers."""

import json

from pydbsec.mcp.helpers import (
    execute_tool,
    get_anthropic_tools,
    parse_balance,
    parse_order_book,
    parse_order_result,
    parse_stock_price,
)
from pydbsec.models.balance import DomesticBalance, OverseasBalance
from pydbsec.models.order import OrderResult
from pydbsec.models.quote import OrderBook, StockPrice


class TestGetAnthropicTools:
    def test_returns_list(self):
        tools = get_anthropic_tools()
        assert isinstance(tools, list)
        assert len(tools) == 6

    def test_tool_structure(self):
        tools = get_anthropic_tools()
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "input_schema" in tool
            assert tool["input_schema"]["type"] == "object"

    def test_tool_names(self):
        tools = get_anthropic_tools()
        names = {t["name"] for t in tools}
        assert names == {
            "get_stock_price",
            "get_balance",
            "get_portfolio_summary",
            "place_order",
            "get_order_book",
            "get_chart",
        }


class TestExecuteTool:
    def test_get_stock_price(self, httpx_mock, monkeypatch):
        monkeypatch.setenv("DBSEC_APP_KEY", "k")
        monkeypatch.setenv("DBSEC_APP_SECRET", "s")
        httpx_mock.add_response(
            url="https://openapi.dbsec.co.kr:8443/oauth2/token",
            method="POST",
            json={"access_token": "tok", "expires_in": 86400, "token_type": "Bearer"},
        )
        httpx_mock.add_response(
            url="https://openapi.dbsec.co.kr:8443/api/v1/quote/kr-stock/inquiry/price",
            method="POST",
            json={
                "rsp_cd": "00000",
                "Out": {
                    "Prpr": "72000",
                    "PrdyVrss": "0",
                    "PrdyCtrt": "0",
                    "AcmlVol": "0",
                    "Oprc": "0",
                    "Hprc": "0",
                    "Lprc": "0",
                },
            },
        )
        result = json.loads(execute_tool("get_stock_price", {"stock_code": "005930"}))
        assert result["current_price"] == 72000

    def test_unknown_tool(self):
        result = json.loads(execute_tool("nonexistent_tool", {}))
        assert "error" in result

    def test_missing_credentials(self, monkeypatch):
        monkeypatch.delenv("DBSEC_APP_KEY", raising=False)
        monkeypatch.delenv("DBSEC_APP_SECRET", raising=False)
        result = json.loads(execute_tool("get_stock_price", {"stock_code": "005930"}))
        assert "error" in result


class TestParseStockPrice:
    def test_from_dict(self):
        data = {
            "current_price": 72000,
            "change": 1500,
            "change_rate": 2.13,
            "volume": 15000000,
            "open": 71000,
            "high": 72500,
            "low": 70500,
        }
        price = parse_stock_price(data)
        assert isinstance(price, StockPrice)
        assert price.current_price == 72000
        assert price.change_rate == 2.13

    def test_from_json_string(self):
        data = json.dumps({"current_price": 180.5, "change": 2.3, "change_rate": 1.29, "volume": 55000000})
        price = parse_stock_price(data)
        assert price.current_price == 180.5


class TestParseBalance:
    def test_domestic(self):
        data = {
            "deposit_total": 10000000,
            "available_cash": 5000000,
            "pnl_amount": 500000,
            "pnl_rate": 5.0,
            "positions": [
                {
                    "stock_code": "A005930",
                    "stock_name": "삼성전자",
                    "quantity": 100,
                    "current_price": 72000,
                    "eval_amount": 7200000,
                    "pnl_amount": 200000,
                    "pnl_rate": 2.86,
                },
            ],
        }
        balance = parse_balance(data, overseas=False)
        assert isinstance(balance, DomesticBalance)
        assert balance.deposit_total == 10000000
        assert len(balance.positions) == 1
        assert balance.positions[0].stock_name == "삼성전자"

    def test_overseas(self):
        data = {
            "deposit_total": 50000,
            "available_cash": 20000,
            "pnl_amount": 5000,
            "pnl_rate": 10.0,
            "positions": [
                {
                    "stock_code": "AAPL",
                    "stock_name": "Apple",
                    "quantity": 10,
                    "current_price": 180.5,
                    "eval_amount": 1805,
                    "pnl_amount": 105,
                    "pnl_rate": 6.18,
                }
            ],
        }
        balance = parse_balance(data, overseas=True)
        assert isinstance(balance, OverseasBalance)
        assert balance.positions[0].stock_code == "AAPL"

    def test_from_json_string(self):
        data = json.dumps(
            {"deposit_total": 1000, "available_cash": 500, "pnl_amount": 0, "pnl_rate": 0, "positions": []}
        )
        balance = parse_balance(data)
        assert isinstance(balance, DomesticBalance)


class TestParseOrderResult:
    def test_success(self):
        data = {"success": True, "order_no": 12345, "message": "정상처리"}
        result = parse_order_result(data)
        assert isinstance(result, OrderResult)
        assert result.success is True
        assert result.order_no == 12345

    def test_from_json_string(self):
        data = json.dumps({"success": False, "order_no": 0, "message": "실패"})
        result = parse_order_result(data)
        assert result.success is False


class TestParseOrderBook:
    def test_basic(self):
        data = {"Out": {"ask1": 72100, "bid1": 72000}}
        ob = parse_order_book(data)
        assert isinstance(ob, OrderBook)
        assert ob.raw["Out"]["ask1"] == 72100

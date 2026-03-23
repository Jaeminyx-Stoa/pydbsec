"""Tests for AsyncPyDBSec client."""

from datetime import datetime, timedelta

import pytest

from pydbsec import AsyncPyDBSec
from pydbsec.models.balance import DomesticBalance, OverseasBalance
from pydbsec.models.order import OrderResult
from pydbsec.models.quote import StockPrice


def _make_async_client() -> AsyncPyDBSec:
    """Create an async client with a pre-set token (no actual API call)."""
    return AsyncPyDBSec(
        "test_key",
        "test_secret",
        token="test_token",
        token_type="Bearer",
        expires_at=datetime.now() + timedelta(hours=1),
    )


class TestAsyncPyDBSec:
    async def test_domestic_balance(self, httpx_mock):
        httpx_mock.add_response(
            url="https://openapi.dbsec.co.kr:8443/api/v1/trading/kr-stock/inquiry/balance",
            method="POST",
            json={
                "rsp_cd": "00000",
                "Out": {
                    "DpsastAmt": "15000000",
                    "OrdAbleAmt": "8000000",
                    "EvalAmt": "12000000",
                    "EvalPnlAmt": "500000",
                    "TotErnrat": "3.45",
                },
                "Out1": [
                    {
                        "IsuNo": "A005930",
                        "IsuNm": "삼성전자",
                        "BalQty0": "50",
                        "NowPrc": "72000",
                        "PchsAmt": "3500000",
                        "EvalAmt": "3600000",
                        "EvalPnlAmt": "100000",
                        "EvalPnlRat": "2.86",
                    },
                ],
            },
        )
        client = _make_async_client()
        balance = await client.domestic.balance()
        assert isinstance(balance, DomesticBalance)
        assert balance.deposit_total == 15000000
        assert len(balance.positions) == 1
        assert balance.positions[0].stock_name == "삼성전자"

    async def test_domestic_price(self, httpx_mock):
        httpx_mock.add_response(
            url="https://openapi.dbsec.co.kr:8443/api/v1/quote/kr-stock/inquiry/price",
            method="POST",
            json={
                "rsp_cd": "00000",
                "Out": {
                    "Prpr": "72000",
                    "PrdyVrss": "1500",
                    "PrdyCtrt": "2.13",
                    "AcmlVol": "15000000",
                    "Oprc": "71000",
                    "Hprc": "72500",
                    "Lprc": "70500",
                },
            },
        )
        client = _make_async_client()
        price = await client.domestic.price("005930")
        assert isinstance(price, StockPrice)
        assert price.current_price == 72000

    async def test_domestic_buy(self, httpx_mock):
        httpx_mock.add_response(
            url="https://openapi.dbsec.co.kr:8443/api/v1/trading/kr-stock/order",
            method="POST",
            json={"rsp_cd": "00000", "rsp_msg": "정상처리", "Out": {"OrdNo": 99999}},
        )
        client = _make_async_client()
        result = await client.domestic.buy("005930", quantity=10, price=70000)
        assert isinstance(result, OrderResult)
        assert result.success is True
        assert result.order_no == 99999

    async def test_overseas_balance(self, httpx_mock):
        httpx_mock.add_response(
            url="https://openapi.dbsec.co.kr:8443/api/v1/trading/overseas-stock/inquiry/balance-margin",
            method="POST",
            json={
                "rsp_cd": "00000",
                "Out": {
                    "DpsastTotAmt": "50000",
                    "OrdAbleAmt": "20000",
                    "EvalAmt": "35000",
                    "EvalPnlAmt": "5000",
                    "TotErnrat": "16.67",
                },
                "Out1": [
                    {
                        "AstkIsuNo": "AAPL",
                        "IsuNm": "Apple Inc",
                        "BalQty": "10",
                        "NowPrc": "180.50",
                        "PchsAmt": "1700",
                        "EvalAmt": "1805",
                        "EvalPnlAmt": "105",
                        "Ernrat": "6.18",
                    }
                ],
            },
        )
        client = _make_async_client()
        balance = await client.overseas.balance()
        assert isinstance(balance, OverseasBalance)
        assert balance.positions[0].stock_code == "AAPL"

    async def test_overseas_price(self, httpx_mock):
        httpx_mock.add_response(
            url="https://openapi.dbsec.co.kr:8443/api/v1/quote/overseas-stock/inquiry/price",
            method="POST",
            json={
                "rsp_cd": "00000",
                "Out": {
                    "Prpr": "180.50",
                    "PrdyVrss": "2.30",
                    "PrdyCtrt": "1.29",
                    "AcmlVol": "55000000",
                    "Oprc": "179.00",
                    "Hprc": "181.20",
                    "Lprc": "178.50",
                },
            },
        )
        client = _make_async_client()
        price = await client.overseas.price("AAPL", market="FN")
        assert isinstance(price, StockPrice)
        assert price.current_price == 180.50

    async def test_context_manager(self, httpx_mock):
        httpx_mock.add_response(
            url="https://openapi.dbsec.co.kr:8443/oauth2/revoke",
            method="POST",
            json={"code": 200, "message": "success"},
        )
        async with _make_async_client() as client:
            assert client.token == "test_token"

    async def test_portfolio_summary(self, httpx_mock):
        httpx_mock.add_response(
            url="https://openapi.dbsec.co.kr:8443/api/v1/trading/kr-stock/inquiry/balance",
            method="POST",
            json={
                "rsp_cd": "00000",
                "Out": {
                    "DpsastAmt": "10000000",
                    "OrdAbleAmt": "5000000",
                    "EvalAmt": "8000000",
                    "EvalPnlAmt": "300000",
                    "TotErnrat": "3.90",
                },
                "Out1": [],
            },
        )
        httpx_mock.add_response(
            url="https://openapi.dbsec.co.kr:8443/api/v1/trading/overseas-stock/inquiry/balance-margin",
            method="POST",
            json={
                "rsp_cd": "00000",
                "Out": {
                    "DpsastTotAmt": "20000",
                    "OrdAbleAmt": "10000",
                    "EvalAmt": "15000",
                    "EvalPnlAmt": "2000",
                    "TotErnrat": "15.38",
                },
                "Out1": [],
            },
        )
        client = _make_async_client()
        summary = await client.portfolio_summary()
        assert summary["total_nav"] == 10000000 + 15000
        assert summary["overseas_nav"] == 15000

    async def test_input_validation_async(self):
        """Async methods should raise ValueError for invalid inputs."""
        client = _make_async_client()
        with pytest.raises(ValueError, match="stock_code must be a non-empty string"):
            await client.domestic.price("")
        with pytest.raises(ValueError, match="quantity must be a positive integer"):
            await client.domestic.buy("005930", quantity=-1, price=70000)
        with pytest.raises(ValueError, match="price must be a non-negative number"):
            await client.domestic.buy("005930", quantity=10, price=-100)

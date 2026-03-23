"""Tests for PyDBSec client integration."""

from datetime import datetime, timedelta

import pytest

from pydbsec import PyDBSec
from pydbsec.models.balance import DomesticBalance, FuturesBalance, OverseasBalance
from pydbsec.models.order import OrderResult
from pydbsec.models.quote import ChartData, OrderBook, StockPrice


def _make_client() -> PyDBSec:
    """Create a client with a pre-set token (no actual API call)."""
    return PyDBSec(
        "test_key",
        "test_secret",
        token="test_token",
        token_type="Bearer",
        expires_at=datetime.now() + timedelta(hours=1),
    )


class TestPyDBSec:
    def test_domestic_balance(self, httpx_mock):
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
        client = _make_client()
        balance = client.domestic.balance()
        assert isinstance(balance, DomesticBalance)
        assert balance.deposit_total == 15000000
        assert len(balance.positions) == 1
        assert balance.positions[0].stock_name == "삼성전자"

    def test_domestic_price(self, httpx_mock):
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
        client = _make_client()
        price = client.domestic.price("005930")
        assert isinstance(price, StockPrice)
        assert price.current_price == 72000
        assert price.change_rate == 2.13

    def test_domestic_buy(self, httpx_mock):
        httpx_mock.add_response(
            url="https://openapi.dbsec.co.kr:8443/api/v1/trading/kr-stock/order",
            method="POST",
            json={"rsp_cd": "00000", "rsp_msg": "정상처리", "Out": {"OrdNo": 99999}},
        )
        client = _make_client()
        result = client.domestic.buy("005930", quantity=10, price=70000)
        assert isinstance(result, OrderResult)
        assert result.success is True
        assert result.order_no == 99999

    def test_overseas_balance(self, httpx_mock):
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
        client = _make_client()
        balance = client.overseas.balance()
        assert isinstance(balance, OverseasBalance)
        assert balance.positions[0].stock_code == "AAPL"

    def test_overseas_price(self, httpx_mock):
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
        client = _make_client()
        price = client.overseas.price("AAPL", market="FN")
        assert isinstance(price, StockPrice)
        assert price.current_price == 180.50

    def test_futures_balance(self, httpx_mock):
        httpx_mock.add_response(
            url="https://openapi.dbsec.co.kr:8443/api/v1/trading/kr-futureoption/inquiry/balance",
            method="POST",
            json={
                "rsp_cd": "00000",
                "Out": {
                    "EvalDpstgTotamt": "5000000",
                    "FnoEvalAmt": "1000000",
                    "EvalPnlAmt": "50000",
                    "ThdayRlzPnlAmt": "10000",
                    "CmsnAmt": "500",
                },
                "Out1": [],
            },
        )
        client = _make_client()
        balance = client.futures.balance()
        assert isinstance(balance, FuturesBalance)
        assert balance.deposit_total == 5000000

    def test_context_manager(self, httpx_mock):
        httpx_mock.add_response(
            url="https://openapi.dbsec.co.kr:8443/oauth2/revoke",
            method="POST",
            json={"code": 200, "message": "success"},
        )
        with _make_client() as client:
            assert client.token == "test_token"
        # Token should be revoked after context exit

    def test_token_properties(self):
        client = _make_client()
        assert client.token == "test_token"
        assert client.token_type == "Bearer"
        assert client.expires_at is not None

    def test_domestic_sell(self, httpx_mock):
        httpx_mock.add_response(
            url="https://openapi.dbsec.co.kr:8443/api/v1/trading/kr-stock/order",
            method="POST",
            json={"rsp_cd": "00000", "rsp_msg": "정상처리", "Out": {"OrdNo": 88888}},
        )
        client = _make_client()
        result = client.domestic.sell("005930", quantity=10, price=72000)
        assert isinstance(result, OrderResult)
        assert result.success is True
        assert result.order_no == 88888

    def test_domestic_cancel(self, httpx_mock):
        httpx_mock.add_response(
            url="https://openapi.dbsec.co.kr:8443/api/v1/trading/kr-stock/order-cancel",
            method="POST",
            json={"rsp_cd": "00000", "rsp_msg": "정상처리", "Out": {"OrdNo": 77777}},
        )
        client = _make_client()
        result = client.domestic.cancel(order_no=99999, stock_code="005930", quantity=10)
        assert isinstance(result, OrderResult)
        assert result.success is True

    def test_domestic_chart(self, httpx_mock):
        httpx_mock.add_response(
            url="https://openapi.dbsec.co.kr:8443/api/v1/quote/kr-chart/day",
            method="POST",
            json={
                "rsp_cd": "00000",
                "Out": {},
                "Out1": [
                    {"TrdDd": "20260320", "Oprc": "71000", "Hprc": "72500", "Lprc": "70500", "Clpr": "72000"},
                    {"TrdDd": "20260319", "Oprc": "70000", "Hprc": "71500", "Lprc": "69500", "Clpr": "71000"},
                ],
            },
        )
        client = _make_client()
        result = client.domestic.chart("005930", period="day", start_date="20260319", end_date="20260320")
        assert isinstance(result, ChartData)
        assert len(result.candles) == 2
        assert result.candles[0].close == 72000
        assert result.candles[0].date == "20260320"
        assert result.raw["Out1"] is not None

    def test_domestic_order_book(self, httpx_mock):
        httpx_mock.add_response(
            url="https://openapi.dbsec.co.kr:8443/api/v1/quote/kr-stock/inquiry/orderbook",
            method="POST",
            json={"rsp_cd": "00000", "Out": {"AskPrc1": "72100", "BidPrc1": "71900"}},
        )
        client = _make_client()
        result = client.domestic.order_book("005930")
        assert isinstance(result, OrderBook)

    def test_overseas_sell(self, httpx_mock):
        httpx_mock.add_response(
            url="https://openapi.dbsec.co.kr:8443/api/v1/trading/overseas-stock/order",
            method="POST",
            json={"rsp_cd": "00000", "rsp_msg": "정상처리", "Out": {"OrdNo": 66666}},
        )
        client = _make_client()
        result = client.overseas.sell("AAPL", quantity=5, price=180.0)
        assert isinstance(result, OrderResult)
        assert result.success is True

    def test_overseas_cancel(self, httpx_mock):
        httpx_mock.add_response(
            url="https://openapi.dbsec.co.kr:8443/api/v1/trading/overseas-stock/order",
            method="POST",
            json={"rsp_cd": "00000", "rsp_msg": "정상처리", "Out": {"OrdNo": 55555}},
        )
        client = _make_client()
        result = client.overseas.cancel(order_no=66666, stock_code="AAPL", quantity=5)
        assert isinstance(result, OrderResult)
        assert result.success is True

    def test_input_validation_errors(self):
        """Sync methods should raise ValueError for invalid inputs."""
        client = _make_client()
        with pytest.raises(ValueError, match="stock_code must be a non-empty string"):
            client.domestic.buy("", quantity=10, price=70000)
        with pytest.raises(ValueError, match="quantity must be a positive integer"):
            client.domestic.sell("005930", quantity=0, price=70000)
        with pytest.raises(ValueError, match="price must be a non-negative number"):
            client.overseas.buy("AAPL", quantity=10, price=-50)
        with pytest.raises(ValueError, match="start_date must be in YYYYMMDD format"):
            client.domestic.trading_history("bad-date", "20260320")
        with pytest.raises(ValueError, match="Invalid period"):
            client.domestic.chart("005930", period="yearly")

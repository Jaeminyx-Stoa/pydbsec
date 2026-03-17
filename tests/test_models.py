"""Tests for Pydantic response models."""

from pydbsec.models.balance import DomesticBalance, FuturesBalance, OverseasBalance
from pydbsec.models.order import OrderResult
from pydbsec.models.quote import StockPrice


class TestDomesticBalance:
    def test_from_api_basic(self):
        data = {
            "Out": {
                "DpsastAmt": "10000000",
                "OrdAbleAmt": "5000000",
                "EvalAmt": "8000000",
                "EvalPnlAmt": "-200000",
                "TotErnrat": "-2.44",
            },
            "Out1": [
                {
                    "IsuNo": "A005930",
                    "IsuNm": "삼성전자",
                    "BalQty0": "100",
                    "NowPrc": "72000",
                    "PchsAmt": "7500000",
                    "EvalAmt": "7200000",
                    "EvalPnlAmt": "-300000",
                    "EvalPnlRat": "-4.00",
                }
            ],
        }
        balance = DomesticBalance.from_api(data)
        assert balance.deposit_total == 10000000
        assert balance.available_cash == 5000000
        assert len(balance.positions) == 1
        assert balance.positions[0].stock_code == "A005930"
        assert balance.positions[0].stock_name == "삼성전자"
        assert balance.positions[0].quantity == 100

    def test_from_api_empty(self):
        data = {"Out": {}, "Out1": []}
        balance = DomesticBalance.from_api(data)
        assert balance.deposit_total == 0
        assert len(balance.positions) == 0


class TestOverseasBalance:
    def test_from_api_basic(self):
        data = {
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
                    "PchsAmt": "1700.00",
                    "EvalAmt": "1805.00",
                    "EvalPnlAmt": "105.00",
                    "Ernrat": "6.18",
                }
            ],
        }
        balance = OverseasBalance.from_api(data)
        assert balance.deposit_total == 50000
        assert len(balance.positions) == 1
        assert balance.positions[0].stock_code == "AAPL"


class TestFuturesBalance:
    def test_from_api(self):
        data = {
            "Out": {
                "EvalDpstgTotamt": "5000000",
                "FnoEvalAmt": "1000000",
                "EvalPnlAmt": "50000",
                "ThdayRlzPnlAmt": "10000",
                "CmsnAmt": "500",
            },
            "Out1": [],
        }
        balance = FuturesBalance.from_api(data)
        assert balance.deposit_total == 5000000
        assert balance.realized_pnl == 10000
        assert balance.commission == 500


class TestOrderResult:
    def test_success(self):
        data = {"rsp_cd": "00000", "rsp_msg": "정상처리", "Out": {"OrdNo": 12345}}
        result = OrderResult.from_api(data)
        assert result.success is True
        assert result.order_no == 12345
        assert result.message == "정상처리"

    def test_failure(self):
        data = {"rsp_cd": "IGW00103", "rsp_msg": "appkey 오류", "Out": {}}
        result = OrderResult.from_api(data)
        assert result.success is False


class TestStockPrice:
    def test_from_api(self):
        data = {
            "Out": {
                "Prpr": "72000",
                "PrdyVrss": "1500",
                "PrdyCtrt": "2.13",
                "AcmlVol": "15000000",
                "Oprc": "71000",
                "Hprc": "72500",
                "Lprc": "70500",
            }
        }
        price = StockPrice.from_api(data)
        assert price.current_price == 72000
        assert price.change == 1500
        assert price.change_rate == 2.13
        assert price.volume == 15000000

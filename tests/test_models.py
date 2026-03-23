"""Tests for Pydantic response models."""

from pydbsec.models.balance import DomesticBalance, FuturesBalance, OverseasBalance
from pydbsec.models.order import OrderResult
from pydbsec.models.quote import ChartCandle, ChartData, OrderBook, StockPrice


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


class TestOrderBook:
    def test_from_api_with_levels(self):
        data = {
            "Out": {
                "AskPrc1": "72100",
                "AskQty1": "500",
                "AskPrc2": "72200",
                "AskQty2": "300",
                "BidPrc1": "71900",
                "BidQty1": "800",
                "BidPrc2": "71800",
                "BidQty2": "400",
                "TotAskQty": "800",
                "TotBidQty": "1200",
            }
        }
        ob = OrderBook.from_api(data)
        assert len(ob.asks) == 2
        assert ob.asks[0].price == 72100
        assert ob.asks[0].volume == 500
        assert len(ob.bids) == 2
        assert ob.bids[0].price == 71900
        assert ob.bids[0].volume == 800
        assert ob.total_ask_volume == 800
        assert ob.total_bid_volume == 1200

    def test_from_api_empty(self):
        data = {"Out": {}}
        ob = OrderBook.from_api(data)
        assert len(ob.asks) == 0
        assert len(ob.bids) == 0
        assert ob.total_ask_volume == 0

    def test_raw_backward_compat(self):
        data = {"Out": {"AskPrc1": "100"}}
        ob = OrderBook.from_api(data)
        assert ob.raw == data


class TestChartCandle:
    def test_from_api_domestic(self):
        item = {
            "TrdDd": "20260320", "Oprc": "71000", "Hprc": "72500",
            "Lprc": "70500", "Clpr": "72000", "AcmlVol": "15000000",
        }
        candle = ChartCandle.from_api(item)
        assert candle.date == "20260320"
        assert candle.open == 71000
        assert candle.high == 72500
        assert candle.low == 70500
        assert candle.close == 72000
        assert candle.volume == 15000000

    def test_from_api_overseas_keys(self):
        item = {
            "TrdDd": "20260320", "OpnPrc": "180.0", "HghPrc": "182.0",
            "LowPrc": "179.0", "ClsPrc": "181.5", "TrdVol": "55000000",
        }
        candle = ChartCandle.from_api(item)
        assert candle.open == 180.0
        assert candle.close == 181.5
        assert candle.volume == 55000000

    def test_from_api_minute_chart(self):
        item = {
            "TrdDd": "20260320", "TrdTm": "100500", "Oprc": "71000",
            "Hprc": "71500", "Lprc": "70900", "Clpr": "71200",
        }
        candle = ChartCandle.from_api(item)
        assert candle.time == "100500"


class TestChartData:
    def test_from_api(self):
        data = {
            "Out": {},
            "Out1": [
                {"TrdDd": "20260320", "Oprc": "71000", "Hprc": "72500", "Lprc": "70500", "Clpr": "72000"},
                {"TrdDd": "20260319", "Oprc": "70000", "Hprc": "71500", "Lprc": "69500", "Clpr": "71000"},
            ],
        }
        chart = ChartData.from_api(data)
        assert len(chart.candles) == 2
        assert chart.candles[0].close == 72000
        assert chart.candles[1].date == "20260319"

    def test_from_api_empty(self):
        data = {"Out": {}, "Out1": []}
        chart = ChartData.from_api(data)
        assert len(chart.candles) == 0

    def test_raw_preserved(self):
        data = {"Out": {"some": "data"}, "Out1": [{"TrdDd": "20260320", "Clpr": "72000"}]}
        chart = ChartData.from_api(data)
        assert chart.raw == data

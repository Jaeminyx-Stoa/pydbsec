"""Tests for portfolio_summary."""

from datetime import datetime, timedelta

from pydbsec import PyDBSec
from pydbsec.models.portfolio import PortfolioSummary


def _make_client() -> PyDBSec:
    return PyDBSec(
        "key",
        "secret",
        token="tok",
        token_type="Bearer",
        expires_at=datetime.now() + timedelta(hours=1),
    )


class TestPortfolioSummary:
    def test_domestic_only(self, httpx_mock):
        httpx_mock.add_response(
            url="https://openapi.dbsec.co.kr:8443/api/v1/trading/kr-stock/inquiry/balance",
            method="POST",
            json={
                "rsp_cd": "00000",
                "Out": {
                    "DpsastAmt": "10000000",
                    "OrdAbleAmt": "3000000",
                    "EvalAmt": "7000000",
                    "EvalPnlAmt": "500000",
                    "TotErnrat": "5.0",
                },
                "Out1": [
                    {
                        "IsuNo": "A005930",
                        "IsuNm": "삼성전자",
                        "BalQty0": "100",
                        "NowPrc": "70000",
                        "PchsAmt": "6500000",
                        "EvalAmt": "7000000",
                        "EvalPnlAmt": "500000",
                        "EvalPnlRat": "7.69",
                    }
                ],
            },
        )
        client = _make_client()
        summary = client.portfolio_summary(include_overseas=False)

        assert isinstance(summary, PortfolioSummary)
        assert summary.total_nav == 10000000
        assert summary.cash == 3000000
        assert summary.profit == 500000
        assert summary.ror == 5.0
        assert len(summary.positions) == 1
        assert summary.positions[0].region == "KR"
        assert summary.positions[0].stock_name == "삼성전자"

    def test_with_overseas(self, httpx_mock):
        # Domestic
        httpx_mock.add_response(
            url="https://openapi.dbsec.co.kr:8443/api/v1/trading/kr-stock/inquiry/balance",
            method="POST",
            json={
                "rsp_cd": "00000",
                "Out": {
                    "DpsastAmt": "10000000",
                    "OrdAbleAmt": "3000000",
                    "EvalAmt": "7000000",
                    "EvalPnlAmt": "500000",
                    "TotErnrat": "5.0",
                },
                "Out1": [],
            },
        )
        # Overseas
        httpx_mock.add_response(
            url="https://openapi.dbsec.co.kr:8443/api/v1/trading/overseas-stock/inquiry/balance-margin",
            method="POST",
            json={
                "rsp_cd": "00000",
                "Out": {
                    "DpsastTotAmt": "5000",
                    "OrdAbleAmt": "2000",
                    "EvalAmt": "3000",
                    "EvalPnlAmt": "300",
                    "TotErnrat": "10.0",
                },
                "Out1": [
                    {
                        "AstkIsuNo": "AAPL",
                        "IsuNm": "Apple",
                        "BalQty": "10",
                        "NowPrc": "180",
                        "PchsAmt": "1700",
                        "EvalAmt": "1800",
                        "EvalPnlAmt": "100",
                        "Ernrat": "5.88",
                    }
                ],
            },
        )
        client = _make_client()
        summary = client.portfolio_summary()

        assert summary.total_nav == 10000000 + 3000  # KR + US eval
        assert summary.cash == 3000000 + 2000
        assert summary.profit == 500000 + 300
        assert summary.overseas_nav == 3000
        assert len(summary.positions) == 1  # 1 US position (0 KR)
        assert summary.positions[0].region == "US"
        assert summary.positions[0].stock_code == "AAPL"

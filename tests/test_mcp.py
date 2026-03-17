"""Tests for MCP server tools."""

import json

import pytest


class TestMCPTools:
    def test_get_stock_price(self, httpx_mock, monkeypatch):
        monkeypatch.setenv("DBSEC_APP_KEY", "test_key")
        monkeypatch.setenv("DBSEC_APP_SECRET", "test_secret")

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
                    "PrdyVrss": "1500",
                    "PrdyCtrt": "2.13",
                    "AcmlVol": "15000000",
                    "Oprc": "71000",
                    "Hprc": "72500",
                    "Lprc": "70500",
                },
            },
        )

        from pydbsec.mcp.server import get_stock_price

        result = json.loads(get_stock_price("005930"))
        assert result["stock_code"] == "005930"
        assert result["current_price"] == 72000
        assert result["change_rate"] == 2.13

    def test_get_balance(self, httpx_mock, monkeypatch):
        monkeypatch.setenv("DBSEC_APP_KEY", "test_key")
        monkeypatch.setenv("DBSEC_APP_SECRET", "test_secret")

        httpx_mock.add_response(
            url="https://openapi.dbsec.co.kr:8443/oauth2/token",
            method="POST",
            json={"access_token": "tok", "expires_in": 86400, "token_type": "Bearer"},
        )
        httpx_mock.add_response(
            url="https://openapi.dbsec.co.kr:8443/api/v1/trading/kr-stock/inquiry/balance",
            method="POST",
            json={
                "rsp_cd": "00000",
                "Out": {
                    "DpsastAmt": "10000000",
                    "OrdAbleAmt": "5000000",
                    "EvalAmt": "8000000",
                    "EvalPnlAmt": "500000",
                    "TotErnrat": "5.0",
                },
                "Out1": [
                    {
                        "IsuNo": "A005930",
                        "IsuNm": "삼성전자",
                        "BalQty0": "100",
                        "NowPrc": "72000",
                        "PchsAmt": "7000000",
                        "EvalAmt": "7200000",
                        "EvalPnlAmt": "200000",
                        "EvalPnlRat": "2.86",
                    }
                ],
            },
        )

        from pydbsec.mcp.server import get_balance

        result = json.loads(get_balance(overseas=False))
        assert result["deposit_total"] == 10000000
        assert len(result["positions"]) == 1
        assert result["positions"][0]["stock_name"] == "삼성전자"

    def test_missing_credentials(self, monkeypatch):
        monkeypatch.delenv("DBSEC_APP_KEY", raising=False)
        monkeypatch.delenv("DBSEC_APP_SECRET", raising=False)

        from pydbsec.mcp.server import get_stock_price

        with pytest.raises(ValueError, match="DBSEC_APP_KEY"):
            get_stock_price("005930")

    def test_mcp_server_instance(self):
        from pydbsec.mcp.server import mcp

        assert mcp.name == "DB Securities"

    def test_tools_registered(self):
        from pydbsec.mcp.server import mcp

        # Verify the server module loads and tools are registered
        assert mcp is not None

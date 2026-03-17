"""Tests for CLI tool."""

from pydbsec.cli import main


class TestCLI:
    def test_no_command_shows_help(self, capsys):
        ret = main([])
        assert ret == 0
        captured = capsys.readouterr()
        assert "pydbsec" in captured.out

    def test_missing_credentials(self, capsys, monkeypatch):
        monkeypatch.delenv("DBSEC_APP_KEY", raising=False)
        monkeypatch.delenv("DBSEC_APP_SECRET", raising=False)
        ret = main(["price", "005930"])
        assert ret == 1
        captured = capsys.readouterr()
        assert "App key and secret required" in captured.err

    def test_price_command(self, httpx_mock, monkeypatch, capsys):
        # Token
        httpx_mock.add_response(
            url="https://openapi.dbsec.co.kr:8443/oauth2/token",
            method="POST",
            json={"access_token": "tok", "expires_in": 86400, "token_type": "Bearer"},
        )
        # Price
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

        monkeypatch.setenv("DBSEC_APP_KEY", "test_key")
        monkeypatch.setenv("DBSEC_APP_SECRET", "test_secret")
        ret = main(["price", "005930"])
        assert ret == 0
        captured = capsys.readouterr()
        assert "72,000" in captured.out
        assert "005930" in captured.out

    def test_price_json_output(self, httpx_mock, monkeypatch, capsys):
        httpx_mock.add_response(
            url="https://openapi.dbsec.co.kr:8443/oauth2/token",
            method="POST",
            json={"access_token": "tok", "expires_in": 86400, "token_type": "Bearer"},
        )
        httpx_mock.add_response(
            url="https://openapi.dbsec.co.kr:8443/api/v1/quote/kr-stock/inquiry/price",
            method="POST",
            json={"rsp_cd": "00000", "Out": {"Prpr": "72000"}},
        )
        monkeypatch.setenv("DBSEC_APP_KEY", "k")
        monkeypatch.setenv("DBSEC_APP_SECRET", "s")
        ret = main(["--json", "price", "005930"])
        assert ret == 0
        captured = capsys.readouterr()
        assert '"Prpr"' in captured.out

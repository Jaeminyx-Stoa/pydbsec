"""Tests for HTTP client."""

from datetime import datetime, timedelta

import pytest

from pydbsec.auth import TokenManager
from pydbsec.exceptions import APIError
from pydbsec.http import HTTPClient


def _make_client(httpx_mock) -> HTTPClient:
    """Create an HTTPClient with a pre-authenticated TokenManager."""
    tm = TokenManager(
        "key",
        "secret",
        token="test_token",
        token_type="Bearer",
        expires_at=datetime.now() + timedelta(hours=1),
    )
    return HTTPClient(tm)


class TestHTTPClient:
    def test_simple_request(self, httpx_mock):
        httpx_mock.add_response(
            url="https://openapi.dbsec.co.kr:8443/api/v1/test",
            method="POST",
            json={"rsp_cd": "00000", "Out": {"value": 42}},
        )
        client = _make_client(httpx_mock)
        result = client.request("/api/v1/test", {"In": {}}, paginate=False)
        assert result["Out"]["value"] == 42

    def test_api_error_raised(self, httpx_mock):
        httpx_mock.add_response(
            url="https://openapi.dbsec.co.kr:8443/api/v1/fail",
            method="POST",
            status_code=400,
            json={"rsp_cd": "IGW00103", "rsp_msg": "Invalid appkey"},
        )
        client = _make_client(httpx_mock)
        with pytest.raises(APIError) as exc_info:
            client.request("/api/v1/fail", paginate=False)
        assert exc_info.value.status_code == 400
        assert exc_info.value.rsp_cd == "IGW00103"

    def test_pagination(self, httpx_mock):
        httpx_mock.add_response(
            url="https://openapi.dbsec.co.kr:8443/api/v1/paged",
            method="POST",
            json={"rsp_cd": "00000", "Out1": [{"id": 1}]},
            headers={"cont_yn": "Y", "cont_key": "page2"},
        )
        httpx_mock.add_response(
            url="https://openapi.dbsec.co.kr:8443/api/v1/paged",
            method="POST",
            json={"rsp_cd": "00000", "Out1": [{"id": 2}]},
            headers={"cont_yn": "N", "cont_key": ""},
        )
        client = _make_client(httpx_mock)
        result = client.request("/api/v1/paged", {"In": {}}, paginate=True)
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["Out1"][0]["id"] == 1
        assert result[1]["Out1"][0]["id"] == 2

    def test_token_refresh_on_igw00121(self, httpx_mock):
        """Should auto-refresh token when IGW00121 (token expired) is returned."""
        # First call returns 500 with IGW00121
        httpx_mock.add_response(
            url="https://openapi.dbsec.co.kr:8443/api/v1/data",
            method="POST",
            status_code=500,
            json={"rsp_cd": "IGW00121", "rsp_msg": "token expired"},
        )
        # Token refresh
        httpx_mock.add_response(
            url="https://openapi.dbsec.co.kr:8443/oauth2/token",
            method="POST",
            json={"access_token": "refreshed_token", "expires_in": 86400, "token_type": "Bearer"},
        )
        # Retry after refresh succeeds
        httpx_mock.add_response(
            url="https://openapi.dbsec.co.kr:8443/api/v1/data",
            method="POST",
            json={"rsp_cd": "00000", "Out": {"ok": True}},
        )

        client = _make_client(httpx_mock)
        result = client.request("/api/v1/data", paginate=False)
        assert result["Out"]["ok"] is True

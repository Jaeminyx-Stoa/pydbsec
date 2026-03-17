"""Tests for WebSocket client."""

import json
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from pydbsec.auth import TokenManager
from pydbsec.ws.client import DBSecWebSocket, _parse_message
from pydbsec.ws.constants import TR_STOCK_EXECUTION, TR_STOCK_ORDERBOOK, WS_URL


def _make_token_manager() -> TokenManager:
    return TokenManager(
        "key",
        "secret",
        token="test_token",
        token_type="Bearer",
        expires_at=datetime.now() + timedelta(hours=1),
    )


class TestWSMessage:
    def test_parse_json_with_header(self):
        raw = json.dumps(
            {
                "header": {"tr_cd": "S00", "tr_type": "0"},
                "body": {"stock_code": "005930", "price": 72000},
            }
        )
        msg = _parse_message(raw)
        assert msg.tr_code == "S00"
        assert msg.data["stock_code"] == "005930"

    def test_parse_json_without_header(self):
        raw = json.dumps({"price": 72000, "volume": 1000})
        msg = _parse_message(raw)
        assert msg.tr_code == ""
        assert msg.data["price"] == 72000

    def test_parse_non_json(self):
        raw = "plain text message"
        msg = _parse_message(raw)
        assert msg.data == "plain text message"

    def test_parse_bytes(self):
        raw = json.dumps({"header": {"tr_cd": "S01"}, "body": {}}).encode("utf-8")
        msg = _parse_message(raw)
        assert msg.tr_code == "S01"


class TestDBSecWebSocket:
    def test_init(self):
        tm = _make_token_manager()
        ws = DBSecWebSocket(tm)
        assert ws.connected is False
        assert len(ws.subscriptions) == 0

    def test_subscribe_before_connect(self):
        """subscribe() before connect() should queue the subscription."""
        import asyncio

        tm = _make_token_manager()
        ws = DBSecWebSocket(tm)

        asyncio.run(ws.subscribe("005930", tr_code="S00"))
        assert ("005930", "S00") in ws.subscriptions

    def test_unsubscribe(self):
        import asyncio

        tm = _make_token_manager()
        ws = DBSecWebSocket(tm)

        asyncio.run(ws.subscribe("005930", tr_code="S00"))
        asyncio.run(ws.unsubscribe("005930", tr_code="S00"))
        assert ("005930", "S00") not in ws.subscriptions

    def test_custom_ws_url(self):
        tm = _make_token_manager()
        ws = DBSecWebSocket(tm, ws_url="wss://custom.example.com:9999")
        assert ws._ws_url == "wss://custom.example.com:9999"

    def test_import_error_without_websockets(self):
        """connect() should raise ImportError with helpful message if websockets not installed."""
        import asyncio

        tm = _make_token_manager()
        ws = DBSecWebSocket(tm)

        with patch.dict("sys.modules", {"websockets": None}):
            with pytest.raises(ImportError, match="pip install pydbsec"):
                asyncio.run(ws.connect())


class TestConstants:
    def test_tr_codes(self):
        assert TR_STOCK_EXECUTION == "S00"
        assert TR_STOCK_ORDERBOOK == "S01"

    def test_ws_url(self):
        assert WS_URL.startswith("wss://")


class TestClientWSProperty:
    def test_pysdbsec_ws_property(self):
        """PyDBSec.ws should return a DBSecWebSocket instance."""
        from pydbsec import PyDBSec

        client = PyDBSec(
            "key",
            "secret",
            token="test_token",
            token_type="Bearer",
            expires_at=datetime.now() + timedelta(hours=1),
        )
        ws = client.ws
        assert isinstance(ws, DBSecWebSocket)
        # Same instance on second access
        assert client.ws is ws

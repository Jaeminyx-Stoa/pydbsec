"""WebSocket client for DB Securities real-time data."""

from __future__ import annotations

import asyncio
import json
import logging
import random
from collections.abc import AsyncIterator
from typing import Any

from ..auth import TokenManager
from ..exceptions import WebSocketError
from .constants import WS_URL
from .models import WSMessage

logger = logging.getLogger("pydbsec.ws")


class DBSecWebSocket:
    """Async WebSocket client for DB Securities real-time market data.

    Usage::

        from pydbsec import PyDBSec

        client = PyDBSec(app_key="...", app_secret="...")

        async with client.ws as ws:
            await ws.subscribe("005930", tr_code="S00")  # 삼성전자 체결가

            async for msg in ws:
                print(msg.tr_code, msg.data)
    """

    def __init__(
        self,
        token_manager: TokenManager,
        *,
        ws_url: str = WS_URL,
        reconnect: bool = True,
        reconnect_delay: float = 3.0,
        max_reconnect_attempts: int = 10,
        heartbeat_interval: float = 30.0,
        queue_maxsize: int = 10000,
    ):
        self._token_manager = token_manager
        self._ws_url = ws_url
        self._reconnect = reconnect
        self._reconnect_delay = reconnect_delay
        self._max_reconnect_attempts = max_reconnect_attempts
        self._heartbeat_interval = heartbeat_interval

        self._ws: Any = None  # websockets.WebSocketClientProtocol
        self._subscriptions: set[tuple[str, str]] = set()  # (stock_code, tr_code)
        self._connected = False
        self._recv_queue: asyncio.Queue[WSMessage] = asyncio.Queue(maxsize=queue_maxsize)
        self._heartbeat_task: asyncio.Task[None] | None = None

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def subscriptions(self) -> set[tuple[str, str]]:
        """Current active subscriptions as (stock_code, tr_code) pairs."""
        return self._subscriptions.copy()

    async def connect(self) -> None:
        """Establish WebSocket connection.

        Requires: ``pip install pydbsec[ws]``
        """
        try:
            import websockets
        except ImportError:
            raise ImportError(
                "websockets is required for real-time data. Install it with: pip install pydbsec[ws]"
            ) from None

        token = self._token_manager.token
        url = f"{self._ws_url}?token={token}"

        logger.info("Connecting to WebSocket: %s", self._ws_url)
        self._ws = await websockets.connect(url)
        self._connected = True
        logger.info("WebSocket connected")

        # Start heartbeat
        if self._heartbeat_task is None or self._heartbeat_task.done():
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

        # Re-subscribe if reconnecting
        for stock_code, tr_code in self._subscriptions:
            await self._send_subscribe(stock_code, tr_code)

    async def disconnect(self) -> None:
        """Close WebSocket connection."""
        self._connected = False
        # Stop heartbeat
        if self._heartbeat_task and not self._heartbeat_task.done():
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
            self._heartbeat_task = None
        if self._ws:
            await self._ws.close()
            self._ws = None
            logger.info("WebSocket disconnected")

    async def subscribe(self, stock_code: str, *, tr_code: str = "S00") -> None:
        """Subscribe to real-time data for a stock.

        Args:
            stock_code: Stock code (e.g., "005930" for domestic, "AAPL" for overseas)
            tr_code: TR code — "S00"=execution, "S01"=orderbook, "IS1"=order filled, etc.
        """
        self._subscriptions.add((stock_code, tr_code))
        if self._connected:
            await self._send_subscribe(stock_code, tr_code)

    async def unsubscribe(self, stock_code: str, *, tr_code: str = "S00") -> None:
        """Unsubscribe from real-time data."""
        self._subscriptions.discard((stock_code, tr_code))
        if self._connected:
            await self._send_unsubscribe(stock_code, tr_code)

    async def _send_subscribe(self, stock_code: str, tr_code: str) -> None:
        msg = {
            "header": {
                "tr_type": "0",  # 0=subscribe, 1=unsubscribe
                "tr_cd": tr_code,
                "token": self._token_manager.token,
            },
            "body": {
                "tr_key": stock_code,
            },
        }
        await self._send(msg)
        logger.info("Subscribed: %s (tr=%s)", stock_code, tr_code)

    async def _send_unsubscribe(self, stock_code: str, tr_code: str) -> None:
        msg = {
            "header": {
                "tr_type": "1",  # unsubscribe
                "tr_cd": tr_code,
                "token": self._token_manager.token,
            },
            "body": {
                "tr_key": stock_code,
            },
        }
        await self._send(msg)
        logger.info("Unsubscribed: %s (tr=%s)", stock_code, tr_code)

    async def _send(self, data: dict[str, Any]) -> None:
        if not self._ws:
            raise RuntimeError("WebSocket is not connected. Call connect() first.")
        await self._ws.send(json.dumps(data))

    async def recv(self) -> WSMessage:
        """Receive a single message from the WebSocket."""
        while True:
            if not self._ws:
                raise RuntimeError("WebSocket is not connected.")

            try:
                raw = await self._ws.recv()
                return _parse_message(raw)
            except Exception as e:
                if self._reconnect:
                    logger.warning("WebSocket recv error: %s, attempting reconnect...", e)
                    await self._try_reconnect()
                else:
                    raise

    async def _heartbeat_loop(self) -> None:
        """Periodically send ping frames to keep connection alive."""
        while self._connected:
            try:
                await asyncio.sleep(self._heartbeat_interval)
                if self._ws and self._connected:
                    await self._ws.ping()
                    logger.debug("Heartbeat ping sent")
            except asyncio.CancelledError:
                raise
            except Exception as e:
                logger.warning("Heartbeat failed: %s", e)
                if self._reconnect and self._connected:
                    self._heartbeat_task = None  # allow connect() to start a new one
                    await self._try_reconnect()
                break

    async def _try_reconnect(self) -> None:
        self._connected = False
        for attempt in range(1, self._max_reconnect_attempts + 1):
            try:
                logger.info("Reconnect attempt %d/%d", attempt, self._max_reconnect_attempts)
                base_delay = self._reconnect_delay * (2 ** (attempt - 1))
                jitter = random.uniform(0, base_delay * 0.5)
                delay = min(base_delay + jitter, 120.0)
                await asyncio.sleep(delay)
                await self.connect()
                return
            except Exception as e:
                logger.warning("Reconnect attempt %d failed: %s", attempt, e)

        raise WebSocketError(f"Failed to reconnect after {self._max_reconnect_attempts} attempts")

    def __aiter__(self) -> AsyncIterator[WSMessage]:
        return self

    async def __anext__(self) -> WSMessage:
        try:
            return await self.recv()
        except (WebSocketError, RuntimeError):
            raise StopAsyncIteration

    async def __aenter__(self) -> DBSecWebSocket:
        await self.connect()
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.disconnect()


def _parse_message(raw: str | bytes) -> WSMessage:
    """Parse a raw WebSocket message into a WSMessage."""
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return WSMessage(data=raw)

    if isinstance(data, dict):
        header = data.get("header", {})
        tr_code = header.get("tr_cd", "") if isinstance(header, dict) else ""
        body = data.get("body", data)
        return WSMessage(tr_code=tr_code, data=body)

    return WSMessage(data=data)

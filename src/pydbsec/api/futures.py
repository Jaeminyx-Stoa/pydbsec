"""Domestic futures/options (국내 선물옵션) API operations."""

from __future__ import annotations

from typing import Any

from ..constants import FUTURES_BALANCE
from ..http import AsyncHTTPClient, HTTPClient
from ..models.balance import FuturesBalance


class FuturesAPI:
    """Domestic futures/options operations — sync."""

    def __init__(self, http: HTTPClient):
        self._http = http

    def balance(self) -> FuturesBalance:
        """Get domestic futures/options balance."""
        data: dict[str, Any] = {"In": {}}
        result = self._http.request(FUTURES_BALANCE, data)
        return FuturesBalance.from_api(result)


class AsyncFuturesAPI:
    """Domestic futures/options operations — async."""

    def __init__(self, http: AsyncHTTPClient):
        self._http = http

    async def balance(self) -> FuturesBalance:
        """Get domestic futures/options balance."""
        data: dict[str, Any] = {"In": {}}
        result = await self._http.request(FUTURES_BALANCE, data)
        return FuturesBalance.from_api(result)

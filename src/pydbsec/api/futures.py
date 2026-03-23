"""Domestic futures/options (국내 선물옵션) API operations."""

from __future__ import annotations

from typing import Any

from .._validation import validate_stock_code
from ..constants import (
    FUTURES_BALANCE,
    FUTURES_FUTURE_TICKER,
    FUTURES_OPTION_BOARD,
    FUTURES_OPTION_DAILY_PRICE,
    FUTURES_OPTION_HOUR_PRICE,
    FUTURES_OPTION_ORDERBOOK,
    FUTURES_OPTION_PRICE,
    FUTURES_OPTION_TICKER,
    MARKET_FUTURES,
    MARKET_OPTIONS_MONTHLY,
    MARKET_OPTIONS_WEEKLY,
)
from ..http import AsyncHTTPClient, HTTPClient
from ..models.balance import FuturesBalance


class FuturesAPI:
    """Domestic futures/options operations — sync."""

    def __init__(self, http: HTTPClient):
        self._http = http

    # ── Trading ──

    def balance(self) -> FuturesBalance:
        """Get domestic futures/options balance."""
        data: dict[str, Any] = {"In": {}}
        result = self._http.request(FUTURES_BALANCE, data)
        return FuturesBalance.from_api(result)

    # ── Quote: Tickers ──

    def option_tickers(self, *, market: str = MARKET_OPTIONS_WEEKLY) -> dict[str, Any]:
        """Get option tickers.

        Args:
            market: "WO"=weekly (default), "OF"=monthly, "OW"=weekly (alt)
        """
        data: dict[str, Any] = {"In": {"InputCondMrktDivCode": market}}
        return self._http.request(FUTURES_OPTION_TICKER, data)

    def future_tickers(self, *, market: str = MARKET_FUTURES) -> dict[str, Any]:
        """Get futures tickers.

        Args:
            market: "FU"=futures (default)
        """
        data: dict[str, Any] = {"In": {"InputCondMrktDivCode": market}}
        return self._http.request(FUTURES_FUTURE_TICKER, data)

    # ── Quote: Prices ──

    def price(self, code: str, *, market: str = MARKET_OPTIONS_WEEKLY) -> dict[str, Any]:
        """Get futures/options current price.

        Args:
            code: Instrument code (e.g., "B09ES887")
            market: "WO"=weekly option, "OF"=monthly option, "FU"=futures
        """
        validate_stock_code(code, label="code")
        data: dict[str, Any] = {"In": {"InputCondMrktDivCode": market, "InputIscd1": code}}
        return self._http.request(FUTURES_OPTION_PRICE, data, paginate=False)

    def orderbook(self, code: str, *, market: str = MARKET_OPTIONS_WEEKLY) -> dict[str, Any]:
        """Get futures/options order book (호가).

        Args:
            code: Instrument code
            market: "WO"=weekly option, "OF"=monthly option, "FU"=futures
        """
        validate_stock_code(code, label="code")
        data: dict[str, Any] = {"In": {"InputCondMrktDivCode": market, "InputIscd1": code}}
        return self._http.request(FUTURES_OPTION_ORDERBOOK, data, paginate=False)

    def daily_price(self, code: str, *, market: str = MARKET_OPTIONS_WEEKLY) -> dict[str, Any]:
        """Get daily price history for futures/options."""
        validate_stock_code(code, label="code")
        data: dict[str, Any] = {"In": {"InputCondMrktDivCode": market, "InputIscd1": code}}
        return self._http.request(FUTURES_OPTION_DAILY_PRICE, data)

    def hour_price(self, code: str, *, market: str = MARKET_OPTIONS_WEEKLY) -> dict[str, Any]:
        """Get intraday price by time for futures/options."""
        validate_stock_code(code, label="code")
        data: dict[str, Any] = {"In": {"InputCondMrktDivCode": market, "InputIscd1": code}}
        return self._http.request(FUTURES_OPTION_HOUR_PRICE, data)

    def option_board(self, *, market: str = MARKET_OPTIONS_MONTHLY) -> dict[str, Any]:
        """Get option board (옵션전광판) — all strikes/expiries at once."""
        data: dict[str, Any] = {"In": {"InputCondMrktDivCode": market}}
        return self._http.request(FUTURES_OPTION_BOARD, data)


class AsyncFuturesAPI:
    """Domestic futures/options operations — async."""

    def __init__(self, http: AsyncHTTPClient):
        self._http = http

    # ── Trading ──

    async def balance(self) -> FuturesBalance:
        """Get domestic futures/options balance."""
        data: dict[str, Any] = {"In": {}}
        result = await self._http.request(FUTURES_BALANCE, data)
        return FuturesBalance.from_api(result)

    # ── Quote: Tickers ──

    async def option_tickers(self, *, market: str = MARKET_OPTIONS_WEEKLY) -> dict[str, Any]:
        """Get option tickers."""
        data: dict[str, Any] = {"In": {"InputCondMrktDivCode": market}}
        return await self._http.request(FUTURES_OPTION_TICKER, data)

    async def future_tickers(self, *, market: str = MARKET_FUTURES) -> dict[str, Any]:
        """Get futures tickers."""
        data: dict[str, Any] = {"In": {"InputCondMrktDivCode": market}}
        return await self._http.request(FUTURES_FUTURE_TICKER, data)

    # ── Quote: Prices ──

    async def price(self, code: str, *, market: str = MARKET_OPTIONS_WEEKLY) -> dict[str, Any]:
        """Get futures/options current price."""
        validate_stock_code(code, label="code")
        data: dict[str, Any] = {"In": {"InputCondMrktDivCode": market, "InputIscd1": code}}
        return await self._http.request(FUTURES_OPTION_PRICE, data, paginate=False)

    async def orderbook(self, code: str, *, market: str = MARKET_OPTIONS_WEEKLY) -> dict[str, Any]:
        """Get futures/options order book (호가)."""
        validate_stock_code(code, label="code")
        data: dict[str, Any] = {"In": {"InputCondMrktDivCode": market, "InputIscd1": code}}
        return await self._http.request(FUTURES_OPTION_ORDERBOOK, data, paginate=False)

    async def daily_price(self, code: str, *, market: str = MARKET_OPTIONS_WEEKLY) -> dict[str, Any]:
        """Get daily price history for futures/options."""
        validate_stock_code(code, label="code")
        data: dict[str, Any] = {"In": {"InputCondMrktDivCode": market, "InputIscd1": code}}
        return await self._http.request(FUTURES_OPTION_DAILY_PRICE, data)

    async def hour_price(self, code: str, *, market: str = MARKET_OPTIONS_WEEKLY) -> dict[str, Any]:
        """Get intraday price by time for futures/options."""
        validate_stock_code(code, label="code")
        data: dict[str, Any] = {"In": {"InputCondMrktDivCode": market, "InputIscd1": code}}
        return await self._http.request(FUTURES_OPTION_HOUR_PRICE, data)

    async def option_board(self, *, market: str = MARKET_OPTIONS_MONTHLY) -> dict[str, Any]:
        """Get option board (옵션전광판)."""
        data: dict[str, Any] = {"In": {"InputCondMrktDivCode": market}}
        return await self._http.request(FUTURES_OPTION_BOARD, data)

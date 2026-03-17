"""Overseas (해외) market API operations."""

from __future__ import annotations

from typing import Any

from ..constants import (
    MARKET_NYSE,
    OVERSEAS_ABLE_ORDER_QTY,
    OVERSEAS_BALANCE,
    OVERSEAS_CHART_DAY,
    OVERSEAS_CHART_MINUTE,
    OVERSEAS_CHART_MONTH,
    OVERSEAS_CHART_WEEK,
    OVERSEAS_DEPOSIT,
    OVERSEAS_ORDER,
    OVERSEAS_ORDER_BOOK,
    OVERSEAS_STOCK_PRICE,
    OVERSEAS_STOCK_TICKER,
    OVERSEAS_TRANSACTION_HISTORY,
)
from ..http import AsyncHTTPClient, HTTPClient
from ..models.balance import OverseasBalance
from ..models.order import OrderResult
from ..models.quote import OrderBook, StockPrice


class OverseasAPI:
    """Overseas (해외) market operations — sync."""

    def __init__(self, http: HTTPClient):
        self._http = http

    # ── Trading ──

    def buy(
        self,
        stock_code: str,
        quantity: int,
        price: float = 0,
        *,
        price_type: str = "1",
        order_condition: str = "1",
    ) -> OrderResult:
        """Place an overseas buy order.

        Args:
            stock_code: Ticker symbol (e.g., "AAPL")
            quantity: Number of shares
            price: Order price (0 for market order)
            price_type: "1"=limit (default)
            order_condition: "1"=normal (default)
        """
        data = _build_overseas_order("2", stock_code, quantity, price, price_type, order_condition, "0", 0)
        result = self._http.request(OVERSEAS_ORDER, data, paginate=False)
        return OrderResult.from_api(result)  # type: ignore[arg-type]

    def sell(
        self,
        stock_code: str,
        quantity: int,
        price: float = 0,
        *,
        price_type: str = "1",
        order_condition: str = "1",
    ) -> OrderResult:
        """Place an overseas sell order."""
        data = _build_overseas_order("1", stock_code, quantity, price, price_type, order_condition, "0", 0)
        result = self._http.request(OVERSEAS_ORDER, data, paginate=False)
        return OrderResult.from_api(result)  # type: ignore[arg-type]

    def cancel(self, order_no: int, stock_code: str, quantity: int) -> OrderResult:
        """Cancel an overseas order."""
        data = _build_overseas_order("1", stock_code, quantity, 0, "1", "1", "2", order_no)
        result = self._http.request(OVERSEAS_ORDER, data, paginate=False)
        return OrderResult.from_api(result)  # type: ignore[arg-type]

    # ── Balance & Account ──

    def balance(
        self,
        *,
        balance_type: str = "2",
        commission_type: str = "1",
        currency_type: str = "2",
        decimal_type: str = "0",
    ) -> OverseasBalance:
        """Get overseas stock balance.

        Args:
            balance_type: "1"=foreign currency, "2"=stock detail (default), "3"=by country, "9"=realized PnL
            commission_type: "0"=none, "1"=buy only (default), "2"=buy+sell
            currency_type: "1"=KRW, "2"=foreign currency (default)
            decimal_type: "0"=all (default), "1"=normal, "2"=fractional
        """
        data = {
            "In": {
                "TrxTpCode": balance_type,
                "CmsnTpCode": commission_type,
                "WonFcurrTpCode": currency_type,
                "DpntBalTpCode": decimal_type,
            }
        }
        result = self._http.request(OVERSEAS_BALANCE, data)
        return OverseasBalance.from_api(result)  # type: ignore[arg-type]

    def deposit(self) -> dict[str, Any]:
        """Get overseas deposit details."""
        result = self._http.request(OVERSEAS_DEPOSIT)
        return result  # type: ignore[return-value]

    def orderable_quantity(
        self,
        stock_code: str,
        price: float,
        *,
        side: str = "2",
        currency_type: str = "2",
    ) -> dict[str, Any]:
        """Get orderable quantity for an overseas stock.

        Args:
            stock_code: Ticker symbol
            price: Order price
            side: "1"=sell, "2"=buy (default)
            currency_type: "1"=KRW, "2"=foreign (default)
        """
        data = {"In": {"TrxTpCode": side, "AstkIsuNo": stock_code, "AstkOrdPrc": price, "WonFcurrTpCode": currency_type}}
        result = self._http.request(OVERSEAS_ABLE_ORDER_QTY, data)
        return result  # type: ignore[return-value]

    # ── History ──

    def transaction_history(
        self,
        start_date: str,
        end_date: str,
        *,
        stock_code: str = "",
        order_type: str = "0",
        execution_status: str = "0",
        sort_type: str = "0",
        query_type: str = "0",
        currency_type: str = "2",
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Get overseas transaction history.

        Args:
            start_date: YYYYMMDD
            end_date: YYYYMMDD
            order_type: "0"=all, "1"=sell, "2"=buy
            execution_status: "0"=all, "1"=filled, "2"=unfilled
            currency_type: "1"=KRW, "2"=foreign (default)
        """
        data = {
            "In": {
                "QrySrtDt": start_date,
                "QryEndDt": end_date,
                "AstkIsuNo": stock_code,
                "AstkBnsTpCode": order_type,
                "OrdxctTpCode": execution_status,
                "StnlnTpCode": sort_type,
                "QryTpCode": query_type,
                "OnlineYn": "0",
                "CvrgOrdYn": "0",
                "WonFcurrTpCode": currency_type,
            }
        }
        return self._http.request(OVERSEAS_TRANSACTION_HISTORY, data)

    # ── Quote ──

    def price(self, stock_code: str, *, market: str = MARKET_NYSE) -> StockPrice:
        """Get current overseas stock price.

        Args:
            stock_code: Ticker symbol (e.g., "AAPL")
            market: "FY"=NYSE (default), "FN"=NASDAQ, "FA"=AMEX
        """
        data = {"In": {"InputCondMrktDivCode": market, "InputIscd1": stock_code}}
        result = self._http.request(OVERSEAS_STOCK_PRICE, data, paginate=False)
        return StockPrice.from_api(result)  # type: ignore[arg-type]

    def order_book(self, stock_code: str, *, market: str = MARKET_NYSE) -> OrderBook:
        """Get overseas order book."""
        data = {"In": {"InputCondMrktDivCode": market, "InputIscd1": stock_code}}
        result = self._http.request(OVERSEAS_ORDER_BOOK, data, paginate=False)
        return OrderBook.from_api(result)  # type: ignore[arg-type]

    def tickers(self, *, market: str = "NY") -> dict[str, Any] | list[dict[str, Any]]:
        """Get overseas stock tickers.

        Args:
            market: "NY"=NYSE, "NA"=NASDAQ, "AM"=AMEX
        """
        data = {"In": {"InputDataCode": market}}
        return self._http.request(OVERSEAS_STOCK_TICKER, data)

    # ── Chart ──

    def chart(
        self,
        stock_code: str,
        *,
        period: str = "day",
        start_date: str = "",
        end_date: str = "",
        time_interval: str = "60",
        market: str = MARKET_NYSE,
        adjust_price: str = "1",
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Get overseas chart data.

        Args:
            stock_code: Ticker symbol
            period: "minute", "day", "week", "month"
            start_date: YYYYMMDD
            end_date: YYYYMMDD
            time_interval: "60"=1min, "300"=5min, "600"=10min, "3600"=60min
            market: "FY"=NYSE, "FN"=NASDAQ, "FA"=AMEX
            adjust_price: "0"=unadjusted, "1"=adjusted (default)
        """
        endpoint, data = _build_overseas_chart(stock_code, period, start_date, end_date, time_interval, market, adjust_price)
        return self._http.request(endpoint, data)


class AsyncOverseasAPI:
    """Overseas (해외) market operations — async."""

    def __init__(self, http: AsyncHTTPClient):
        self._http = http

    async def buy(self, stock_code: str, quantity: int, price: float = 0, *, price_type: str = "1", order_condition: str = "1") -> OrderResult:
        data = _build_overseas_order("2", stock_code, quantity, price, price_type, order_condition, "0", 0)
        result = await self._http.request(OVERSEAS_ORDER, data, paginate=False)
        return OrderResult.from_api(result)  # type: ignore[arg-type]

    async def sell(self, stock_code: str, quantity: int, price: float = 0, *, price_type: str = "1", order_condition: str = "1") -> OrderResult:
        data = _build_overseas_order("1", stock_code, quantity, price, price_type, order_condition, "0", 0)
        result = await self._http.request(OVERSEAS_ORDER, data, paginate=False)
        return OrderResult.from_api(result)  # type: ignore[arg-type]

    async def cancel(self, order_no: int, stock_code: str, quantity: int) -> OrderResult:
        data = _build_overseas_order("1", stock_code, quantity, 0, "1", "1", "2", order_no)
        result = await self._http.request(OVERSEAS_ORDER, data, paginate=False)
        return OrderResult.from_api(result)  # type: ignore[arg-type]

    async def balance(self, *, balance_type: str = "2", commission_type: str = "1", currency_type: str = "2", decimal_type: str = "0") -> OverseasBalance:
        data = {"In": {"TrxTpCode": balance_type, "CmsnTpCode": commission_type, "WonFcurrTpCode": currency_type, "DpntBalTpCode": decimal_type}}
        result = await self._http.request(OVERSEAS_BALANCE, data)
        return OverseasBalance.from_api(result)  # type: ignore[arg-type]

    async def deposit(self) -> dict[str, Any]:
        result = await self._http.request(OVERSEAS_DEPOSIT)
        return result  # type: ignore[return-value]

    async def orderable_quantity(self, stock_code: str, price: float, *, side: str = "2", currency_type: str = "2") -> dict[str, Any]:
        data = {"In": {"TrxTpCode": side, "AstkIsuNo": stock_code, "AstkOrdPrc": price, "WonFcurrTpCode": currency_type}}
        result = await self._http.request(OVERSEAS_ABLE_ORDER_QTY, data)
        return result  # type: ignore[return-value]

    async def transaction_history(
        self, start_date: str, end_date: str, *, stock_code: str = "", order_type: str = "0",
        execution_status: str = "0", sort_type: str = "0", query_type: str = "0", currency_type: str = "2",
    ) -> dict[str, Any] | list[dict[str, Any]]:
        data = {
            "In": {
                "QrySrtDt": start_date, "QryEndDt": end_date, "AstkIsuNo": stock_code,
                "AstkBnsTpCode": order_type, "OrdxctTpCode": execution_status, "StnlnTpCode": sort_type,
                "QryTpCode": query_type, "OnlineYn": "0", "CvrgOrdYn": "0", "WonFcurrTpCode": currency_type,
            }
        }
        return await self._http.request(OVERSEAS_TRANSACTION_HISTORY, data)

    async def price(self, stock_code: str, *, market: str = MARKET_NYSE) -> StockPrice:
        data = {"In": {"InputCondMrktDivCode": market, "InputIscd1": stock_code}}
        result = await self._http.request(OVERSEAS_STOCK_PRICE, data, paginate=False)
        return StockPrice.from_api(result)  # type: ignore[arg-type]

    async def order_book(self, stock_code: str, *, market: str = MARKET_NYSE) -> OrderBook:
        data = {"In": {"InputCondMrktDivCode": market, "InputIscd1": stock_code}}
        result = await self._http.request(OVERSEAS_ORDER_BOOK, data, paginate=False)
        return OrderBook.from_api(result)  # type: ignore[arg-type]

    async def tickers(self, *, market: str = "NY") -> dict[str, Any] | list[dict[str, Any]]:
        data = {"In": {"InputDataCode": market}}
        return await self._http.request(OVERSEAS_STOCK_TICKER, data)

    async def chart(
        self, stock_code: str, *, period: str = "day", start_date: str = "", end_date: str = "",
        time_interval: str = "60", market: str = MARKET_NYSE, adjust_price: str = "1",
    ) -> dict[str, Any] | list[dict[str, Any]]:
        endpoint, data = _build_overseas_chart(stock_code, period, start_date, end_date, time_interval, market, adjust_price)
        return await self._http.request(endpoint, data)


# ── Helpers ──


def _build_overseas_order(
    side: str, stock_code: str, quantity: int, price: float,
    price_type: str, order_condition: str, trade_type: str, original_order_no: int,
) -> dict[str, Any]:
    return {
        "In": {
            "AstkIsuNo": stock_code,
            "AstkBnsTpCode": side,
            "AstkOrdprcPtnCode": price_type,
            "AstkOrdCndiTpCode": order_condition,
            "AstkOrdQty": quantity,
            "AstkOrdPrc": price,
            "OrdTrdTpCode": trade_type,
            "OrgOrdNo": original_order_no,
        }
    }


def _build_overseas_chart(
    stock_code: str, period: str, start_date: str, end_date: str,
    time_interval: str, market: str, adjust_price: str,
) -> tuple[str, dict[str, Any]]:
    base_in: dict[str, Any] = {
        "InputCondMrktDivCode": market,
        "InputOrgAdjPrc": adjust_price,
        "InputIscd1": stock_code,
    }

    if period == "minute":
        base_in.update({
            "InputPwDataIncuYn": "Y",
            "InputHourClsCode": "0",
            "InputDate1": start_date,
            "InputDate2": end_date,
            "InputDivXtick": time_interval,
        })
        return OVERSEAS_CHART_MINUTE, {"In": base_in}
    elif period == "day":
        base_in["InputDate1"] = start_date
        base_in["InputDate2"] = end_date
        return OVERSEAS_CHART_DAY, {"In": base_in}
    elif period == "week":
        base_in.update({"InputDate1": start_date, "InputDate2": end_date, "InputPeriodDivCode": "W"})
        return OVERSEAS_CHART_WEEK, {"In": base_in}
    elif period == "month":
        base_in.update({"InputDate1": start_date, "InputDate2": end_date, "InputPeriodDivCode": "M"})
        return OVERSEAS_CHART_MONTH, {"In": base_in}
    else:
        raise ValueError(f"Invalid period: {period!r}. Must be 'minute', 'day', 'week', or 'month'.")

"""Domestic (국내) market API operations."""

from __future__ import annotations

from typing import Any

from ..constants import (
    DOMESTIC_ABLE_ORDER_QTY,
    DOMESTIC_BALANCE,
    DOMESTIC_CANCEL_ORDER,
    DOMESTIC_CHART_DAY,
    DOMESTIC_CHART_MINUTE,
    DOMESTIC_CHART_MONTH,
    DOMESTIC_CHART_WEEK,
    DOMESTIC_DAILY_TRADE_REPORT,
    DOMESTIC_DEPOSIT,
    DOMESTIC_ORDER,
    DOMESTIC_ORDER_BOOK,
    DOMESTIC_STOCK_PRICE,
    DOMESTIC_STOCK_TICKER,
    DOMESTIC_TRADING_HISTORY,
    DOMESTIC_TRANSACTION_HISTORY,
)
from ..http import AsyncHTTPClient, HTTPClient
from ..models.balance import DomesticBalance
from ..models.order import OrderResult
from ..models.quote import OrderBook, StockPrice


class DomesticAPI:
    """Domestic (국내) market operations — sync."""

    def __init__(self, http: HTTPClient):
        self._http = http

    # ── Trading ──

    def buy(
        self,
        stock_code: str,
        quantity: int,
        price: float = 0,
        *,
        price_type: str = "00",
        credit_type: str = "000",
        loan_date: str = "00000000",
        order_condition: str = "0",
    ) -> OrderResult:
        """Place a buy order.

        Args:
            stock_code: Stock code (e.g., "005930")
            quantity: Number of shares to buy
            price: Order price. 0 for market order.
            price_type: "00"=limit (default), "03"=market
            credit_type: "000"=normal (default)
            loan_date: "00000000"=normal order (default)
            order_condition: "0"=none (default)
        """
        data = _build_domestic_order("2", stock_code, quantity, price, price_type, credit_type, loan_date, order_condition)
        result = self._http.request(DOMESTIC_ORDER, data, paginate=False)
        return OrderResult.from_api(result)  # type: ignore[arg-type]

    def sell(
        self,
        stock_code: str,
        quantity: int,
        price: float = 0,
        *,
        price_type: str = "00",
        credit_type: str = "000",
        loan_date: str = "00000000",
        order_condition: str = "0",
    ) -> OrderResult:
        """Place a sell order."""
        data = _build_domestic_order("1", stock_code, quantity, price, price_type, credit_type, loan_date, order_condition)
        result = self._http.request(DOMESTIC_ORDER, data, paginate=False)
        return OrderResult.from_api(result)  # type: ignore[arg-type]

    def cancel(self, order_no: int, stock_code: str, quantity: int) -> OrderResult:
        """Cancel an existing order."""
        data = {"In": {"OrgOrdNo": order_no, "IsuNo": stock_code, "OrdQty": quantity}}
        result = self._http.request(DOMESTIC_CANCEL_ORDER, data, paginate=False)
        return OrderResult.from_api(result)  # type: ignore[arg-type]

    # ── Balance & Account ──

    def balance(self, *, query_type: str = "2") -> DomesticBalance:
        """Get domestic stock balance.

        Args:
            query_type: "0"=all, "1"=exclude unlisted, "2"=exclude unlisted/KONEX/KOTC (default)
        """
        data = {"In": {"QryTpCode": query_type}}
        result = self._http.request(DOMESTIC_BALANCE, data)
        return DomesticBalance.from_api(result)  # type: ignore[arg-type]

    def deposit(self) -> dict[str, Any]:
        """Get account deposit info."""
        result = self._http.request(DOMESTIC_DEPOSIT)
        return result  # type: ignore[return-value]

    def orderable_quantity(self, stock_code: str, price: float, *, side: str = "2") -> dict[str, Any]:
        """Get orderable quantity for a stock.

        Args:
            stock_code: Stock code
            price: Order price
            side: "1"=sell, "2"=buy (default)
        """
        isu_no = f"A{stock_code}" if not stock_code.startswith("A") else stock_code
        data = {"In": {"BnsTpCode": side, "IsuNo": isu_no, "OrdPrc": price}}
        result = self._http.request(DOMESTIC_ABLE_ORDER_QTY, data)
        return result  # type: ignore[return-value]

    # ── History ──

    def transaction_history(
        self,
        *,
        execution_status: str = "0",
        order_type: str = "0",
        stock_type: str = "0",
        query_type: str = "0",
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Get today's transaction history (체결/미체결 내역).

        Args:
            execution_status: "0"=all, "1"=filled, "2"=unfilled
            order_type: "0"=all, "1"=sell, "2"=buy
        """
        data = {
            "In": {
                "ExecYn": execution_status,
                "BnsTpCode": order_type,
                "IsuTpCode": stock_type,
                "QryTp": query_type,
                "TrdMktCode": "0",
                "SorTpYn": "2",
            }
        }
        return self._http.request(DOMESTIC_TRANSACTION_HISTORY, data)

    def trading_history(self, start_date: str, end_date: str, *, query_type: str = "0") -> dict[str, Any] | list[dict[str, Any]]:
        """Get trading history for a date range.

        Args:
            start_date: Start date (YYYYMMDD)
            end_date: End date (YYYYMMDD)
            query_type: "0"=all, "1"=deposit/withdraw, "2"=in/out, "3"=trades, "4"=transfer
        """
        data = {"In": {"QryTp": query_type, "QrySrtDt": start_date, "QryEndDt": end_date, "SrtNo": 0, "IsuNo": ""}}
        return self._http.request(DOMESTIC_TRADING_HISTORY, data)

    def daily_trade_report(self, date: str, *, stock_code: str = "") -> dict[str, Any] | list[dict[str, Any]]:
        """Get daily trade report.

        Args:
            date: Trade date (YYYYMMDD)
            stock_code: Specific stock code, or empty for all
        """
        data = {"In": {"IsuNo": stock_code, "BnsDt": date}}
        return self._http.request(DOMESTIC_DAILY_TRADE_REPORT, data)

    # ── Quote ──

    def price(self, stock_code: str, *, market: str = "UJ") -> StockPrice:
        """Get current stock price.

        Args:
            stock_code: Stock code (e.g., "005930")
            market: "UJ"=stock (default), "E"=ETF, "EN"=ETN
        """
        data = {"In": {"InputCondMrktDivCode": market, "InputIscd1": stock_code}}
        result = self._http.request(DOMESTIC_STOCK_PRICE, data, paginate=False)
        return StockPrice.from_api(result)  # type: ignore[arg-type]

    def order_book(self, stock_code: str, *, market: str = "UJ") -> OrderBook:
        """Get order book (호가)."""
        data = {"In": {"InputCondMrktDivCode": market, "InputIscd1": stock_code}}
        result = self._http.request(DOMESTIC_ORDER_BOOK, data, paginate=False)
        return OrderBook.from_api(result)  # type: ignore[arg-type]

    def tickers(self, *, market: str = "UJ") -> dict[str, Any] | list[dict[str, Any]]:
        """Get stock tickers list."""
        data = {"In": {"InputCondMrktDivCode": market, "InputIscd1": None}}
        return self._http.request(DOMESTIC_STOCK_TICKER, data)

    # ── Chart ──

    def chart(
        self,
        stock_code: str,
        *,
        period: str = "day",
        start_date: str = "",
        end_date: str = "",
        time_interval: str = "60",
        market: str = "UJ",
        adjust_price: str = "0",
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Get chart data.

        Args:
            stock_code: Stock code
            period: "minute", "day", "week", "month"
            start_date: Start date (YYYYMMDD)
            end_date: End date (YYYYMMDD), required for day/week/month
            time_interval: For minute charts — "60"=1min, "300"=5min, "600"=10min
            market: Market code
            adjust_price: "0"=adjusted (default), "1"=unadjusted
        """
        endpoint, data = _build_domestic_chart(stock_code, period, start_date, end_date, time_interval, market, adjust_price)
        return self._http.request(endpoint, data)


class AsyncDomesticAPI:
    """Domestic (국내) market operations — async."""

    def __init__(self, http: AsyncHTTPClient):
        self._http = http

    async def buy(
        self,
        stock_code: str,
        quantity: int,
        price: float = 0,
        *,
        price_type: str = "00",
        credit_type: str = "000",
        loan_date: str = "00000000",
        order_condition: str = "0",
    ) -> OrderResult:
        data = _build_domestic_order("2", stock_code, quantity, price, price_type, credit_type, loan_date, order_condition)
        result = await self._http.request(DOMESTIC_ORDER, data, paginate=False)
        return OrderResult.from_api(result)  # type: ignore[arg-type]

    async def sell(
        self,
        stock_code: str,
        quantity: int,
        price: float = 0,
        *,
        price_type: str = "00",
        credit_type: str = "000",
        loan_date: str = "00000000",
        order_condition: str = "0",
    ) -> OrderResult:
        data = _build_domestic_order("1", stock_code, quantity, price, price_type, credit_type, loan_date, order_condition)
        result = await self._http.request(DOMESTIC_ORDER, data, paginate=False)
        return OrderResult.from_api(result)  # type: ignore[arg-type]

    async def cancel(self, order_no: int, stock_code: str, quantity: int) -> OrderResult:
        data = {"In": {"OrgOrdNo": order_no, "IsuNo": stock_code, "OrdQty": quantity}}
        result = await self._http.request(DOMESTIC_CANCEL_ORDER, data, paginate=False)
        return OrderResult.from_api(result)  # type: ignore[arg-type]

    async def balance(self, *, query_type: str = "2") -> DomesticBalance:
        data = {"In": {"QryTpCode": query_type}}
        result = await self._http.request(DOMESTIC_BALANCE, data)
        return DomesticBalance.from_api(result)  # type: ignore[arg-type]

    async def deposit(self) -> dict[str, Any]:
        result = await self._http.request(DOMESTIC_DEPOSIT)
        return result  # type: ignore[return-value]

    async def orderable_quantity(self, stock_code: str, price: float, *, side: str = "2") -> dict[str, Any]:
        isu_no = f"A{stock_code}" if not stock_code.startswith("A") else stock_code
        data = {"In": {"BnsTpCode": side, "IsuNo": isu_no, "OrdPrc": price}}
        result = await self._http.request(DOMESTIC_ABLE_ORDER_QTY, data)
        return result  # type: ignore[return-value]

    async def transaction_history(
        self, *, execution_status: str = "0", order_type: str = "0", stock_type: str = "0", query_type: str = "0"
    ) -> dict[str, Any] | list[dict[str, Any]]:
        data = {
            "In": {
                "ExecYn": execution_status,
                "BnsTpCode": order_type,
                "IsuTpCode": stock_type,
                "QryTp": query_type,
                "TrdMktCode": "0",
                "SorTpYn": "2",
            }
        }
        return await self._http.request(DOMESTIC_TRANSACTION_HISTORY, data)

    async def trading_history(self, start_date: str, end_date: str, *, query_type: str = "0") -> dict[str, Any] | list[dict[str, Any]]:
        data = {"In": {"QryTp": query_type, "QrySrtDt": start_date, "QryEndDt": end_date, "SrtNo": 0, "IsuNo": ""}}
        return await self._http.request(DOMESTIC_TRADING_HISTORY, data)

    async def daily_trade_report(self, date: str, *, stock_code: str = "") -> dict[str, Any] | list[dict[str, Any]]:
        data = {"In": {"IsuNo": stock_code, "BnsDt": date}}
        return await self._http.request(DOMESTIC_DAILY_TRADE_REPORT, data)

    async def price(self, stock_code: str, *, market: str = "UJ") -> StockPrice:
        data = {"In": {"InputCondMrktDivCode": market, "InputIscd1": stock_code}}
        result = await self._http.request(DOMESTIC_STOCK_PRICE, data, paginate=False)
        return StockPrice.from_api(result)  # type: ignore[arg-type]

    async def order_book(self, stock_code: str, *, market: str = "UJ") -> OrderBook:
        data = {"In": {"InputCondMrktDivCode": market, "InputIscd1": stock_code}}
        result = await self._http.request(DOMESTIC_ORDER_BOOK, data, paginate=False)
        return OrderBook.from_api(result)  # type: ignore[arg-type]

    async def tickers(self, *, market: str = "UJ") -> dict[str, Any] | list[dict[str, Any]]:
        data = {"In": {"InputCondMrktDivCode": market, "InputIscd1": None}}
        return await self._http.request(DOMESTIC_STOCK_TICKER, data)

    async def chart(
        self,
        stock_code: str,
        *,
        period: str = "day",
        start_date: str = "",
        end_date: str = "",
        time_interval: str = "60",
        market: str = "UJ",
        adjust_price: str = "0",
    ) -> dict[str, Any] | list[dict[str, Any]]:
        endpoint, data = _build_domestic_chart(stock_code, period, start_date, end_date, time_interval, market, adjust_price)
        return await self._http.request(endpoint, data)


# ── Helpers ──


def _build_domestic_order(
    side: str, stock_code: str, quantity: int, price: float,
    price_type: str, credit_type: str, loan_date: str, order_condition: str,
) -> dict[str, Any]:
    return {
        "In": {
            "IsuNo": stock_code,
            "OrdQty": quantity,
            "OrdPrc": price,
            "BnsTpCode": side,
            "OrdprcPtnCode": price_type,
            "MgntrnCode": credit_type,
            "LoanDt": loan_date,
            "OrdCndiTpCode": order_condition,
            "TrchNo": 1,
        }
    }


def _build_domestic_chart(
    stock_code: str, period: str, start_date: str, end_date: str,
    time_interval: str, market: str, adjust_price: str,
) -> tuple[str, dict[str, Any]]:
    base_in: dict[str, Any] = {
        "InputCondMrktDivCode": market,
        "InputOrgAdjPrc": adjust_price,
        "InputIscd1": stock_code,
    }

    if period == "minute":
        base_in["InputDate1"] = start_date
        base_in["InputDivXtick"] = time_interval
        return DOMESTIC_CHART_MINUTE, {"In": base_in}
    elif period == "day":
        base_in["InputDate1"] = start_date
        base_in["InputDate2"] = end_date
        return DOMESTIC_CHART_DAY, {"In": base_in}
    elif period == "week":
        base_in["InputDate1"] = start_date
        base_in["InputDate2"] = end_date
        base_in["InputPeriodDivCode"] = "W"
        return DOMESTIC_CHART_WEEK, {"In": base_in}
    elif period == "month":
        base_in["InputDate1"] = start_date
        base_in["InputDate2"] = end_date
        base_in["InputPeriodDivCode"] = "M"
        return DOMESTIC_CHART_MONTH, {"In": base_in}
    else:
        raise ValueError(f"Invalid period: {period!r}. Must be 'minute', 'day', 'week', or 'month'.")

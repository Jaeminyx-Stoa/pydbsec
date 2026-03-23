"""Quote (price, orderbook, chart) models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

__all__ = ["StockPrice", "OrderBookLevel", "OrderBook", "ChartCandle", "ChartData"]


class StockPrice(BaseModel):
    """Current stock price information."""

    current_price: float = Field(default=0, description="Current price")
    change: float = Field(default=0, description="Price change from previous close")
    change_rate: float = Field(default=0, description="Change rate (%)")
    volume: int = Field(default=0, description="Trading volume")
    open_price: float = Field(default=0, description="Open price")
    high_price: float = Field(default=0, description="High price")
    low_price: float = Field(default=0, description="Low price")

    raw: dict[str, Any] = Field(default_factory=dict, description="Raw API response data", exclude=True)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> StockPrice:
        out = data.get("Out", {})
        return cls(
            current_price=float(out.get("Prpr", out.get("NowPrc", 0))),
            change=float(out.get("PrdyVrss", out.get("Cmpprevddprc", 0))),
            change_rate=float(out.get("PrdyCtrt", out.get("Cmpprevddrat", 0))),
            volume=int(out.get("AcmlVol", out.get("TrdVol", 0))),
            open_price=float(out.get("Oprc", out.get("OpnPrc", 0))),
            high_price=float(out.get("Hprc", out.get("HghPrc", 0))),
            low_price=float(out.get("Lprc", out.get("LowPrc", 0))),
            raw=data,
        )


class OrderBookLevel(BaseModel):
    """Single price level in an order book."""

    price: float = Field(default=0, description="Price at this level")
    volume: int = Field(default=0, description="Volume at this level")


class OrderBook(BaseModel):
    """Order book (호가) data."""

    asks: list[OrderBookLevel] = Field(default_factory=list, description="Ask (sell) levels, best ask first")
    bids: list[OrderBookLevel] = Field(default_factory=list, description="Bid (buy) levels, best bid first")
    total_ask_volume: int = Field(default=0, description="Total ask volume")
    total_bid_volume: int = Field(default=0, description="Total bid volume")

    raw: dict[str, Any] = Field(default_factory=dict, description="Raw API response data")

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> OrderBook:
        out = data.get("Out", {})
        asks: list[OrderBookLevel] = []
        bids: list[OrderBookLevel] = []
        for i in range(1, 11):
            ask_price = float(out.get(f"AskPrc{i}", out.get(f"AstkAskPrc{i}", 0)) or 0)
            ask_vol = int(out.get(f"AskQty{i}", out.get(f"AstkAskQty{i}", 0)) or 0)
            if ask_price > 0 or ask_vol > 0:
                asks.append(OrderBookLevel(price=ask_price, volume=ask_vol))
            bid_price = float(out.get(f"BidPrc{i}", out.get(f"AstkBidPrc{i}", 0)) or 0)
            bid_vol = int(out.get(f"BidQty{i}", out.get(f"AstkBidQty{i}", 0)) or 0)
            if bid_price > 0 or bid_vol > 0:
                bids.append(OrderBookLevel(price=bid_price, volume=bid_vol))
        return cls(
            asks=asks,
            bids=bids,
            total_ask_volume=int(out.get("TotAskQty", 0) or 0),
            total_bid_volume=int(out.get("TotBidQty", 0) or 0),
            raw=data,
        )


class ChartCandle(BaseModel):
    """Single OHLCV candle record."""

    date: str = Field(default="", description="Trade date (YYYYMMDD)")
    time: str = Field(default="", description="Trade time (for minute charts)")
    open: float = Field(default=0, description="Open price")
    high: float = Field(default=0, description="High price")
    low: float = Field(default=0, description="Low price")
    close: float = Field(default=0, description="Close price")
    volume: int = Field(default=0, description="Trading volume")

    raw: dict[str, Any] = Field(default_factory=dict, description="Raw candle data", exclude=True)

    @classmethod
    def from_api(cls, item: dict[str, Any]) -> ChartCandle:
        return cls(
            date=str(item.get("TrdDd") or ""),
            time=str(item.get("TrdTm") or ""),
            open=float(item.get("Oprc", item.get("OpnPrc", 0)) or 0),
            high=float(item.get("Hprc", item.get("HghPrc", 0)) or 0),
            low=float(item.get("Lprc", item.get("LowPrc", 0)) or 0),
            close=float(item.get("Clpr", item.get("ClsPrc", 0)) or 0),
            volume=int(item.get("AcmlVol", item.get("TrdVol", 0)) or 0),
            raw=item,
        )


class ChartData(BaseModel):
    """Chart data containing OHLCV candles."""

    candles: list[ChartCandle] = Field(default_factory=list, description="OHLCV candle records")

    raw: dict[str, Any] = Field(default_factory=dict, description="Raw API response data", exclude=True)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ChartData:
        items = data.get("Out1", [])
        candles = [ChartCandle.from_api(item) for item in items] if isinstance(items, list) else []
        return cls(candles=candles, raw=data)

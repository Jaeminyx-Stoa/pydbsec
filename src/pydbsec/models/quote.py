"""Quote (price, orderbook) models."""

from __future__ import annotations

from pydantic import BaseModel, Field

__all__ = ["StockPrice", "OrderBook"]


class StockPrice(BaseModel):
    """Current stock price information."""

    current_price: float = Field(default=0, description="Current price")
    change: float = Field(default=0, description="Price change from previous close")
    change_rate: float = Field(default=0, description="Change rate (%)")
    volume: int = Field(default=0, description="Trading volume")
    open_price: float = Field(default=0, description="Open price")
    high_price: float = Field(default=0, description="High price")
    low_price: float = Field(default=0, description="Low price")

    raw: dict = Field(default_factory=dict, description="Raw API response data", exclude=True)

    @classmethod
    def from_api(cls, data: dict) -> StockPrice:
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


class OrderBook(BaseModel):
    """Order book (호가) data."""

    raw: dict = Field(default_factory=dict, description="Raw API response data")

    @classmethod
    def from_api(cls, data: dict) -> OrderBook:
        return cls(raw=data)

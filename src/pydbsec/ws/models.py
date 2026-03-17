"""Models for real-time WebSocket data."""

from __future__ import annotations

from pydantic import BaseModel, Field

__all__ = ["RealtimeTick", "RealtimeOrderBook", "WSMessage"]


class RealtimeTick(BaseModel):
    """Real-time stock execution (체결) data."""

    tr_code: str = Field(description="TR code (e.g., S00)")
    stock_code: str = Field(default="", description="Stock code")
    price: float = Field(default=0, description="Current/execution price")
    change: float = Field(default=0, description="Price change")
    change_rate: float = Field(default=0, description="Change rate (%)")
    volume: int = Field(default=0, description="Execution volume")
    timestamp: str = Field(default="", description="Execution time")

    raw: dict | str = Field(default_factory=dict, description="Raw message data", exclude=True)


class RealtimeOrderBook(BaseModel):
    """Real-time order book (호가) data."""

    tr_code: str = Field(description="TR code (e.g., S01)")
    stock_code: str = Field(default="", description="Stock code")
    timestamp: str = Field(default="", description="Time")

    raw: dict | str = Field(default_factory=dict, description="Raw message data", exclude=True)


class WSMessage(BaseModel):
    """Generic WebSocket message wrapper."""

    tr_code: str = Field(default="", description="TR code")
    data: dict | str | list = Field(default_factory=dict, description="Message payload")

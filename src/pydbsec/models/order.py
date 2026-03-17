"""Order-related models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

__all__ = ["OrderResult"]


class OrderResult(BaseModel):
    """Result of a buy/sell/cancel order."""

    success: bool = Field(description="Whether the order was accepted")
    order_no: int = Field(default=0, description="Order number assigned by the exchange")
    message: str = Field(default="", description="Response message")

    raw: dict[str, Any] = Field(default_factory=dict, description="Raw API response data", exclude=True)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> OrderResult:
        rsp_cd = str(data.get("rsp_cd", ""))
        out = data.get("Out", {})
        return cls(
            success=rsp_cd == "00000",
            order_no=int(out.get("OrdNo", 0)),
            message=str(data.get("rsp_msg", "")),
            raw=data,
        )

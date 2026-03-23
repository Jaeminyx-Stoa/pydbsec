"""Portfolio summary models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

__all__ = ["PortfolioPosition", "PortfolioSummary"]


class PortfolioPosition(BaseModel):
    """A single position in the unified portfolio."""

    region: str = Field(description="Market region ('KR' or 'US')")
    stock_code: str = Field(default="", description="Stock code or ticker")
    stock_name: str = Field(default="", description="Stock name")
    quantity: int = Field(default=0, description="Holding quantity")
    current_price: float = Field(default=0, description="Current price")
    eval_amount: float = Field(default=0, description="Evaluation amount")
    pnl_amount: float = Field(default=0, description="Unrealized P&L")
    pnl_rate: float = Field(default=0, description="P&L rate (%)")


class PortfolioSummary(BaseModel):
    """Unified portfolio summary across domestic and overseas markets."""

    total_nav: float = Field(default=0, description="Total Net Asset Value")
    cash: float = Field(default=0, description="Available cash")
    profit: float = Field(default=0, description="Total unrealized P&L")
    ror: float = Field(default=0, description="Rate of return (%)")
    overseas_nav: float = Field(default=0, description="Overseas NAV (0 if not included)")
    positions: list[PortfolioPosition] = Field(default_factory=list, description="Combined positions")

    raw: dict[str, Any] = Field(default_factory=dict, description="Raw data", exclude=True)

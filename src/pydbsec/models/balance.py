"""Balance response models."""

from __future__ import annotations

from pydantic import BaseModel, Field

__all__ = [
    "DomesticBalance",
    "DomesticPosition",
    "OverseasBalance",
    "OverseasPosition",
    "FuturesBalance",
    "FuturesPosition",
]


class DomesticPosition(BaseModel):
    """A single domestic stock position."""

    stock_code: str = Field(description="Stock code (with 'A' prefix from API)")
    stock_name: str = Field(default="", description="Stock name")
    quantity: int = Field(default=0, description="Holding quantity")
    current_price: float = Field(default=0, description="Current price")
    purchase_amount: float = Field(default=0, description="Total purchase amount")
    eval_amount: float = Field(default=0, description="Current evaluation amount")
    pnl_amount: float = Field(default=0, description="Unrealized P&L amount")
    pnl_rate: float = Field(default=0, description="Unrealized P&L rate (%)")

    raw: dict = Field(default_factory=dict, description="Raw API response data", exclude=True)

    @classmethod
    def from_api(cls, data: dict) -> DomesticPosition:
        return cls(
            stock_code=str(data.get("IsuNo", "")),
            stock_name=str(data.get("IsuNm", "")),
            quantity=int(data.get("BalQty0", data.get("BalQty", 0))),
            current_price=float(data.get("NowPrc", 0)),
            purchase_amount=float(data.get("PchsAmt", 0)),
            eval_amount=float(data.get("EvalAmt", 0)),
            pnl_amount=float(data.get("EvalPnlAmt", 0)),
            pnl_rate=float(data.get("EvalPnlRat", data.get("Ernrat", 0))),
            raw=data,
        )


class DomesticBalance(BaseModel):
    """Domestic stock balance summary."""

    deposit_total: float = Field(default=0, description="Total deposit amount")
    available_cash: float = Field(default=0, description="Available cash for orders")
    eval_total: float = Field(default=0, description="Total evaluation amount")
    pnl_amount: float = Field(default=0, description="Total unrealized P&L")
    pnl_rate: float = Field(default=0, description="Total P&L rate (%)")
    positions: list[DomesticPosition] = Field(default_factory=list, description="Stock positions")

    raw: dict = Field(default_factory=dict, description="Raw API response data", exclude=True)

    @classmethod
    def from_api(cls, data: dict) -> DomesticBalance:
        summary = data.get("Out", {})
        stocks = data.get("Out1", [])
        return cls(
            deposit_total=float(summary.get("DpsastAmt", summary.get("EvalDpstgTotamt", 0))),
            available_cash=float(summary.get("OrdAbleAmt", summary.get("MnyOrdAbleAmt", 0))),
            eval_total=float(summary.get("EvalAmt", summary.get("BalEvalAmt", 0))),
            pnl_amount=float(summary.get("EvalPnlAmt", 0)),
            pnl_rate=float(summary.get("TotErnrat", summary.get("Ernrat", 0))),
            positions=[DomesticPosition.from_api(s) for s in stocks],
            raw=data,
        )


class OverseasPosition(BaseModel):
    """A single overseas stock position."""

    stock_code: str = Field(description="Stock ticker symbol")
    stock_name: str = Field(default="", description="Stock name")
    quantity: int = Field(default=0, description="Holding quantity")
    current_price: float = Field(default=0, description="Current price")
    purchase_amount: float = Field(default=0, description="Total purchase amount")
    eval_amount: float = Field(default=0, description="Current evaluation amount")
    pnl_amount: float = Field(default=0, description="Unrealized P&L amount")
    pnl_rate: float = Field(default=0, description="Unrealized P&L rate (%)")

    raw: dict = Field(default_factory=dict, description="Raw API response data", exclude=True)

    @classmethod
    def from_api(cls, data: dict) -> OverseasPosition:
        return cls(
            stock_code=str(data.get("AstkIsuNo", data.get("IsuNo", ""))),
            stock_name=str(data.get("IsuNm", "")),
            quantity=int(data.get("BalQty", 0)),
            current_price=float(data.get("NowPrc", 0)),
            purchase_amount=float(data.get("PchsAmt", 0)),
            eval_amount=float(data.get("EvalAmt", 0)),
            pnl_amount=float(data.get("EvalPnlAmt", 0)),
            pnl_rate=float(data.get("Ernrat", 0)),
            raw=data,
        )


class OverseasBalance(BaseModel):
    """Overseas stock balance summary."""

    deposit_total: float = Field(default=0, description="Total deposit")
    available_cash: float = Field(default=0, description="Available cash")
    eval_total: float = Field(default=0, description="Total evaluation")
    pnl_amount: float = Field(default=0, description="Total unrealized P&L")
    pnl_rate: float = Field(default=0, description="Total P&L rate (%)")
    positions: list[OverseasPosition] = Field(default_factory=list, description="Stock positions")

    raw: dict = Field(default_factory=dict, description="Raw API response data", exclude=True)

    @classmethod
    def from_api(cls, data: dict) -> OverseasBalance:
        summary = data.get("Out", {})
        stocks = data.get("Out1", data.get("Out2", []))
        return cls(
            deposit_total=float(summary.get("DpsastTotAmt", summary.get("DpsastAmt", 0))),
            available_cash=float(summary.get("OrdAbleAmt", 0)),
            eval_total=float(summary.get("EvalAmt", summary.get("BalEvalAmt", 0))),
            pnl_amount=float(summary.get("EvalPnlAmt", 0)),
            pnl_rate=float(summary.get("TotErnrat", 0)),
            positions=[OverseasPosition.from_api(s) for s in stocks],
            raw=data,
        )


class FuturesPosition(BaseModel):
    """A single futures position."""

    stock_code: str = Field(description="Futures contract code")
    stock_name: str = Field(default="", description="Contract name")
    quantity: int = Field(default=0, description="Holding quantity")
    current_price: float = Field(default=0, description="Current price")
    eval_amount: float = Field(default=0, description="Evaluation amount")
    pnl_amount: float = Field(default=0, description="Unrealized P&L")

    raw: dict = Field(default_factory=dict, description="Raw API response data", exclude=True)

    @classmethod
    def from_api(cls, data: dict) -> FuturesPosition:
        return cls(
            stock_code=str(data.get("IsuNo", "")),
            stock_name=str(data.get("IsuNm", "")),
            quantity=int(data.get("BalQty", 0)),
            current_price=float(data.get("NowPrc", 0)),
            eval_amount=float(data.get("EvalAmt", data.get("FnoEvalAmt", 0))),
            pnl_amount=float(data.get("EvalPnlAmt", 0)),
            raw=data,
        )


class FuturesBalance(BaseModel):
    """Domestic futures/options balance."""

    deposit_total: float = Field(default=0, description="Total deposit")
    eval_amount: float = Field(default=0, description="Evaluation amount")
    pnl_amount: float = Field(default=0, description="Unrealized P&L")
    realized_pnl: float = Field(default=0, description="Today's realized P&L")
    commission: float = Field(default=0, description="Commission")
    positions: list[FuturesPosition] = Field(default_factory=list)

    raw: dict = Field(default_factory=dict, description="Raw API response data", exclude=True)

    @classmethod
    def from_api(cls, data: dict) -> FuturesBalance:
        summary = data.get("Out", {})
        stocks = data.get("Out1", [])
        return cls(
            deposit_total=float(summary.get("EvalDpstgTotamt", 0)),
            eval_amount=float(summary.get("FnoEvalAmt", 0)),
            pnl_amount=float(summary.get("EvalPnlAmt", 0)),
            realized_pnl=float(summary.get("ThdayRlzPnlAmt", 0)),
            commission=float(summary.get("CmsnAmt", 0)),
            positions=[FuturesPosition.from_api(s) for s in stocks],
            raw=data,
        )

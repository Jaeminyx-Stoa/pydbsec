"""pydbsec — Python wrapper for DB Securities (DB증권) OpenAPI.

Usage::

    from pydbsec import PyDBSec

    client = PyDBSec(app_key="YOUR_KEY", app_secret="YOUR_SECRET")

    # Get domestic balance
    balance = client.domestic.balance()

    # Get stock price
    price = client.domestic.price("005930")
"""

from .client import AsyncPyDBSec, PyDBSec
from .exceptions import (
    APIError,
    InsufficientBalanceError,
    InvalidOrderError,
    PyDBSecError,
    RateLimitError,
    TokenError,
    TokenExpiredError,
    ValidationError,
    WebSocketError,
)

__all__ = [
    "PyDBSec",
    "AsyncPyDBSec",
    "PyDBSecError",
    "TokenError",
    "TokenExpiredError",
    "APIError",
    "RateLimitError",
    "InvalidOrderError",
    "InsufficientBalanceError",
    "WebSocketError",
    "ValidationError",
]

__version__ = "1.0.0"

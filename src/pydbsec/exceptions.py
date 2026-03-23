"""Custom exceptions for pydbsec."""

from __future__ import annotations

from typing import Any


class PyDBSecError(Exception):
    """Base exception for pydbsec."""


class TokenError(PyDBSecError):
    """Raised when token acquisition or refresh fails."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        response_body: dict[str, Any] | str | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class TokenExpiredError(TokenError):
    """Raised when the token has expired and auto-refresh failed."""


class APIError(PyDBSecError):
    """Raised when an API request fails."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        rsp_cd: str | None = None,
        response_body: dict[str, Any] | str | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.rsp_cd = rsp_cd
        self.response_body = response_body


class RateLimitError(APIError):
    """Raised when an API request is rate-limited (HTTP 429)."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        rsp_cd: str | None = None,
        response_body: dict[str, Any] | str | None = None,
        retry_after: float | None = None,
    ):
        super().__init__(message, status_code=status_code, rsp_cd=rsp_cd, response_body=response_body)
        self.retry_after = retry_after


class InvalidOrderError(APIError):
    """Raised when an order request fails (invalid parameters, market closed, etc.)."""


class InsufficientBalanceError(APIError):
    """Raised when an order fails due to insufficient balance or margin."""


class WebSocketError(PyDBSecError):
    """Raised for WebSocket connection and communication failures."""


class ValidationError(PyDBSecError, ValueError):
    """Raised for input validation failures.

    Inherits from both PyDBSecError and ValueError for backward compatibility
    with code that catches ValueError.
    """

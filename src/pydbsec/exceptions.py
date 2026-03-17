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


class TokenExpiredError(TokenError):
    """Raised when the token has expired and auto-refresh failed."""

"""Main client classes for pydbsec."""

from __future__ import annotations

from datetime import datetime

from .api.domestic import AsyncDomesticAPI, DomesticAPI
from .api.futures import AsyncFuturesAPI, FuturesAPI
from .api.overseas import AsyncOverseasAPI, OverseasAPI
from .auth import TokenManager
from .http import AsyncHTTPClient, HTTPClient


class PyDBSec:
    """Synchronous client for DB Securities OpenAPI.

    Usage::

        from pydbsec import PyDBSec

        client = PyDBSec(app_key="YOUR_KEY", app_secret="YOUR_SECRET")

        # Domestic balance
        balance = client.domestic.balance()
        print(balance.deposit_total, balance.positions)

        # Stock price
        price = client.domestic.price("005930")
        print(price.current_price)

        # Buy order
        result = client.domestic.buy("005930", quantity=10, price=70000)

        # Overseas
        us_balance = client.overseas.balance()

        # Close session (revokes token)
        client.close()
    """

    def __init__(
        self,
        app_key: str,
        app_secret: str,
        *,
        token: str | None = None,
        token_type: str | None = None,
        expires_at: datetime | None = None,
        timeout: float = 30,
    ):
        """Initialize PyDBSec client.

        Args:
            app_key: DB Securities API app key
            app_secret: DB Securities API app secret
            token: Existing access token (optional, for reuse)
            token_type: Token type (e.g., "Bearer")
            expires_at: Token expiration datetime
            timeout: HTTP request timeout in seconds
        """
        self._token_manager = TokenManager(
            app_key,
            app_secret,
            token=token,
            token_type=token_type,
            expires_at=expires_at,
        )
        self._http = HTTPClient(self._token_manager, timeout=timeout)

        self.domestic = DomesticAPI(self._http)
        self.overseas = OverseasAPI(self._http)
        self.futures = FuturesAPI(self._http)

    @property
    def token(self) -> str:
        """Current access token."""
        return self._token_manager.token

    @property
    def token_type(self) -> str | None:
        """Token type (e.g., 'Bearer')."""
        return self._token_manager.token_type

    @property
    def expires_at(self) -> datetime | None:
        """Token expiration datetime."""
        return self._token_manager.expires_at

    def close(self) -> None:
        """Revoke the access token and close the session."""
        self._token_manager.revoke()

    def __enter__(self) -> PyDBSec:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


class AsyncPyDBSec:
    """Asynchronous client for DB Securities OpenAPI.

    Usage::

        from pydbsec import AsyncPyDBSec

        async def main():
            client = AsyncPyDBSec(app_key="YOUR_KEY", app_secret="YOUR_SECRET")

            balance = await client.domestic.balance()
            price = await client.domestic.price("005930")

            client.close()
    """

    def __init__(
        self,
        app_key: str,
        app_secret: str,
        *,
        token: str | None = None,
        token_type: str | None = None,
        expires_at: datetime | None = None,
        timeout: float = 30,
    ):
        self._token_manager = TokenManager(
            app_key,
            app_secret,
            token=token,
            token_type=token_type,
            expires_at=expires_at,
        )
        self._http = AsyncHTTPClient(self._token_manager, timeout=timeout)

        self.domestic = AsyncDomesticAPI(self._http)
        self.overseas = AsyncOverseasAPI(self._http)
        self.futures = AsyncFuturesAPI(self._http)

    @property
    def token(self) -> str:
        return self._token_manager.token

    @property
    def token_type(self) -> str | None:
        return self._token_manager.token_type

    @property
    def expires_at(self) -> datetime | None:
        return self._token_manager.expires_at

    def close(self) -> None:
        self._token_manager.revoke()

    async def __aenter__(self) -> AsyncPyDBSec:
        return self

    async def __aexit__(self, *args: object) -> None:
        self.close()

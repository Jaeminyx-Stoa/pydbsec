"""Main client classes for pydbsec."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ws import DBSecWebSocket

from .api.domestic import AsyncDomesticAPI, DomesticAPI
from .api.futures import AsyncFuturesAPI, FuturesAPI
from .api.overseas import AsyncOverseasAPI, OverseasAPI
from .auth import TokenManager
from .constants import BASE_URL
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

        # Close session (revokes token, closes connection pool)
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
        base_url: str = BASE_URL,
        timeout: float = 30,
    ):
        """Initialize PyDBSec client.

        Args:
            app_key: DB Securities API app key
            app_secret: DB Securities API app secret
            token: Existing access token (optional, for reuse)
            token_type: Token type (e.g., "Bearer")
            expires_at: Token expiration datetime
            base_url: API base URL (override for sandbox/testing)
            timeout: HTTP request timeout in seconds
        """
        self._token_manager = TokenManager(
            app_key,
            app_secret,
            base_url=base_url,
            token=token,
            token_type=token_type,
            expires_at=expires_at,
        )
        self._http = HTTPClient(self._token_manager, base_url=base_url, timeout=timeout)

        self.domestic = DomesticAPI(self._http)
        self.overseas = OverseasAPI(self._http)
        self.futures = FuturesAPI(self._http)
        self._ws: DBSecWebSocket | None = None

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

    @property
    def ws(self) -> DBSecWebSocket:
        """WebSocket client for real-time data.

        Requires: ``pip install pydbsec[ws]``

        Usage::

            async with client.ws as ws:
                await ws.subscribe("005930", tr_code="S00")
                async for msg in ws:
                    print(msg.data)
        """
        if self._ws is None:
            from .ws import DBSecWebSocket
            from .ws.constants import WS_URL

            self._ws = DBSecWebSocket(self._token_manager, ws_url=WS_URL)
        return self._ws

    def close(self) -> None:
        """Revoke the access token and close the connection pool."""
        self._http.close()
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
            async with AsyncPyDBSec(app_key="YOUR_KEY", app_secret="YOUR_SECRET") as client:
                balance = await client.domestic.balance()
                price = await client.domestic.price("005930")
    """

    def __init__(
        self,
        app_key: str,
        app_secret: str,
        *,
        token: str | None = None,
        token_type: str | None = None,
        expires_at: datetime | None = None,
        base_url: str = BASE_URL,
        timeout: float = 30,
    ):
        self._token_manager = TokenManager(
            app_key,
            app_secret,
            base_url=base_url,
            token=token,
            token_type=token_type,
            expires_at=expires_at,
        )
        self._http = AsyncHTTPClient(self._token_manager, base_url=base_url, timeout=timeout)

        self.domestic = AsyncDomesticAPI(self._http)
        self.overseas = AsyncOverseasAPI(self._http)
        self.futures = AsyncFuturesAPI(self._http)
        self._ws: DBSecWebSocket | None = None

    @property
    def token(self) -> str:
        return self._token_manager.token

    @property
    def token_type(self) -> str | None:
        return self._token_manager.token_type

    @property
    def expires_at(self) -> datetime | None:
        return self._token_manager.expires_at

    @property
    def ws(self) -> DBSecWebSocket:
        """WebSocket client for real-time data."""
        if self._ws is None:
            from .ws import DBSecWebSocket
            from .ws.constants import WS_URL

            self._ws = DBSecWebSocket(self._token_manager, ws_url=WS_URL)
        return self._ws

    async def aclose(self) -> None:
        """Close the async connection pool and revoke token."""
        await self._http.aclose()
        self._token_manager.revoke()

    def close(self) -> None:
        """Revoke token (sync). For full cleanup use aclose()."""
        self._token_manager.revoke()

    async def __aenter__(self) -> AsyncPyDBSec:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.aclose()

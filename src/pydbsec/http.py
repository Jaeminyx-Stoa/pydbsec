"""HTTP client with automatic pagination and token refresh."""

from __future__ import annotations

import logging
import time
from typing import Any

import httpx

from .auth import TokenManager
from .constants import BASE_URL
from .exceptions import APIError

logger = logging.getLogger("pydbsec")

_MAX_CONTINUATION = 100
_CONTINUATION_DELAY = 1.5


class HTTPClient:
    """Synchronous HTTP client for DB Securities API."""

    def __init__(self, token_manager: TokenManager, *, timeout: float = 30):
        self._token_manager = token_manager
        self._timeout = timeout

    def request(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        *,
        paginate: bool = True,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Make a POST request to the API.

        All DB Securities API calls use POST method.
        When paginate=True, automatically follows cont_yn/cont_key pagination.
        Returns a single dict for single-page results, or a list of dicts for multi-page.
        """
        return self._request_with_pagination(endpoint, data, paginate=paginate)

    def _request_with_pagination(
        self,
        endpoint: str,
        data: dict[str, Any] | None,
        *,
        paginate: bool,
        cont_yn: str = "N",
        cont_key: str | None = None,
        _pages: list[dict[str, Any]] | None = None,
        _page_count: int = 0,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        url = f"{BASE_URL}{endpoint}"

        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Authorization": self._token_manager.authorization,
        }
        if cont_yn:
            headers["cont_yn"] = cont_yn
        if cont_key:
            headers["cont_key"] = cont_key

        logger.debug("POST %s data=%s", endpoint, data)

        response = httpx.post(url, json=data, headers=headers, timeout=self._timeout)

        # Handle token expiry (IGW00121)
        if 500 <= response.status_code < 600:
            body = _safe_json(response)
            if isinstance(body, dict) and body.get("rsp_cd") == "IGW00121":
                logger.info("Token expired (IGW00121), refreshing...")
                self._token_manager.refresh()
                headers["Authorization"] = self._token_manager.authorization
                time.sleep(1.5)
                response = httpx.post(url, json=data, headers=headers, timeout=self._timeout)

        if response.status_code >= 400:
            body = _safe_json(response)
            rsp_cd = body.get("rsp_cd") if isinstance(body, dict) else None
            raise APIError(
                f"API request failed: {endpoint} (HTTP {response.status_code})",
                status_code=response.status_code,
                rsp_cd=rsp_cd,
                response_body=body,
            )

        result: dict[str, Any] = response.json()

        # Handle pagination
        if paginate:
            resp_cont_yn = response.headers.get("cont_yn", "N")
            resp_cont_key = response.headers.get("cont_key", "")

            if resp_cont_yn == "Y" and resp_cont_key and _page_count < _MAX_CONTINUATION:
                pages = (_pages or []) + [result]
                time.sleep(_CONTINUATION_DELAY)
                return self._request_with_pagination(
                    endpoint,
                    data,
                    paginate=True,
                    cont_yn=resp_cont_yn,
                    cont_key=resp_cont_key,
                    _pages=pages,
                    _page_count=_page_count + 1,
                )

            if _pages:
                return _pages + [result]

        return result


class AsyncHTTPClient:
    """Asynchronous HTTP client for DB Securities API."""

    def __init__(self, token_manager: TokenManager, *, timeout: float = 30):
        self._token_manager = token_manager
        self._timeout = timeout

    async def request(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        *,
        paginate: bool = True,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        return await self._request_with_pagination(endpoint, data, paginate=paginate)

    async def _request_with_pagination(
        self,
        endpoint: str,
        data: dict[str, Any] | None,
        *,
        paginate: bool,
        cont_yn: str = "N",
        cont_key: str | None = None,
        _pages: list[dict[str, Any]] | None = None,
        _page_count: int = 0,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        import asyncio

        url = f"{BASE_URL}{endpoint}"

        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Authorization": self._token_manager.authorization,
        }
        if cont_yn:
            headers["cont_yn"] = cont_yn
        if cont_key:
            headers["cont_key"] = cont_key

        logger.debug("POST %s data=%s", endpoint, data)

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(url, json=data, headers=headers)

            # Handle token expiry (IGW00121)
            if 500 <= response.status_code < 600:
                body = _safe_json(response)
                if isinstance(body, dict) and body.get("rsp_cd") == "IGW00121":
                    logger.info("Token expired (IGW00121), refreshing...")
                    self._token_manager.refresh()
                    headers["Authorization"] = self._token_manager.authorization
                    await asyncio.sleep(1.5)
                    response = await client.post(url, json=data, headers=headers)

            if response.status_code >= 400:
                body = _safe_json(response)
                rsp_cd = body.get("rsp_cd") if isinstance(body, dict) else None
                raise APIError(
                    f"API request failed: {endpoint} (HTTP {response.status_code})",
                    status_code=response.status_code,
                    rsp_cd=rsp_cd,
                    response_body=body,
                )

            result: dict[str, Any] = response.json()

        # Handle pagination
        if paginate:
            resp_cont_yn = response.headers.get("cont_yn", "N")
            resp_cont_key = response.headers.get("cont_key", "")

            if resp_cont_yn == "Y" and resp_cont_key and _page_count < _MAX_CONTINUATION:
                pages = (_pages or []) + [result]
                await asyncio.sleep(_CONTINUATION_DELAY)
                return await self._request_with_pagination(
                    endpoint,
                    data,
                    paginate=True,
                    cont_yn=resp_cont_yn,
                    cont_key=resp_cont_key,
                    _pages=pages,
                    _page_count=_page_count + 1,
                )

            if _pages:
                return _pages + [result]

        return result


def _safe_json(response: httpx.Response) -> dict[str, Any] | str:
    try:
        return response.json()  # type: ignore[no-any-return]
    except Exception:
        return response.text

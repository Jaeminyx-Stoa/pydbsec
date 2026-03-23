"""HTTP client with connection pooling, rate limiting, pagination, and token refresh."""

from __future__ import annotations

import logging
import time
from typing import Any

import httpx

from .auth import TokenManager
from .constants import BALANCE_ERROR_CODES, BASE_URL, ERROR_TOKEN_EXPIRED, ORDER_ERROR_CODES
from .exceptions import APIError, InsufficientBalanceError, InvalidOrderError, RateLimitError
from .ratelimit import RateLimiter

logger = logging.getLogger("pydbsec")

_MAX_CONTINUATION = 100
_CONTINUATION_DELAY = 1.5

# Keys in API responses that contain list data (paginated)
_LIST_KEYS = ("Out1", "Out2", "Out3")


class HTTPClient:
    """Synchronous HTTP client with connection pooling and rate limiting."""

    def __init__(
        self,
        token_manager: TokenManager,
        *,
        base_url: str = BASE_URL,
        timeout: float = 30,
        rate_limiter: RateLimiter | None = None,
    ):
        self._token_manager = token_manager
        self._base_url = base_url
        self._client = httpx.Client(base_url=base_url, timeout=timeout)
        self._rate_limiter = rate_limiter

    def request(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        *,
        paginate: bool = True,
    ) -> dict[str, Any]:
        """Make a POST request to the API.

        All DB Securities API calls use POST method.
        When paginate=True, automatically follows cont_yn/cont_key pagination
        and merges all pages into a single dict.
        """
        return self._request_impl(endpoint, data, paginate=paginate)

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        self._client.close()

    def _request_impl(
        self,
        endpoint: str,
        data: dict[str, Any] | None,
        *,
        paginate: bool,
        cont_yn: str = "N",
        cont_key: str | None = None,
        _accumulated: dict[str, Any] | None = None,
        _page_count: int = 0,
    ) -> dict[str, Any]:
        if self._rate_limiter:
            self._rate_limiter.wait(endpoint)

        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Authorization": self._token_manager.authorization,
        }
        if cont_yn:
            headers["cont_yn"] = cont_yn
        if cont_key:
            headers["cont_key"] = cont_key

        logger.debug("POST %s data=%s", endpoint, data)

        response = self._client.post(endpoint, json=data, headers=headers)

        # Handle token expiry (IGW00121)
        if 500 <= response.status_code < 600:
            body = _safe_json(response)
            if isinstance(body, dict) and body.get("rsp_cd") == ERROR_TOKEN_EXPIRED:
                logger.info("Token expired (IGW00121), refreshing...")
                self._token_manager.refresh()
                headers["Authorization"] = self._token_manager.authorization
                time.sleep(1.5)
                response = self._client.post(endpoint, json=data, headers=headers)

        if response.status_code >= 400:
            body = _safe_json(response)
            rsp_cd = body.get("rsp_cd") if isinstance(body, dict) else None
            raise _classify_error(
                endpoint=endpoint,
                status_code=response.status_code,
                rsp_cd=rsp_cd,
                response_body=body,
                retry_after=response.headers.get("Retry-After"),
            )

        result: dict[str, Any] = response.json()

        # Merge pagination results into a single dict
        if paginate:
            merged = _merge_page(result, _accumulated)

            resp_cont_yn = response.headers.get("cont_yn", "N")
            resp_cont_key = response.headers.get("cont_key", "")

            if resp_cont_yn == "Y" and resp_cont_key and _page_count < _MAX_CONTINUATION:
                time.sleep(_CONTINUATION_DELAY)
                return self._request_impl(
                    endpoint,
                    data,
                    paginate=True,
                    cont_yn=resp_cont_yn,
                    cont_key=resp_cont_key,
                    _accumulated=merged,
                    _page_count=_page_count + 1,
                )

            return merged

        return result


class AsyncHTTPClient:
    """Asynchronous HTTP client with connection pooling and rate limiting."""

    def __init__(
        self,
        token_manager: TokenManager,
        *,
        base_url: str = BASE_URL,
        timeout: float = 30,
        rate_limiter: RateLimiter | None = None,
    ):
        self._token_manager = token_manager
        self._base_url = base_url
        self._client = httpx.AsyncClient(base_url=base_url, timeout=timeout)
        self._rate_limiter = rate_limiter

    async def request(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        *,
        paginate: bool = True,
    ) -> dict[str, Any]:
        return await self._request_impl(endpoint, data, paginate=paginate)

    async def aclose(self) -> None:
        """Close the underlying async HTTP connection pool."""
        await self._client.aclose()

    async def _request_impl(
        self,
        endpoint: str,
        data: dict[str, Any] | None,
        *,
        paginate: bool,
        cont_yn: str = "N",
        cont_key: str | None = None,
        _accumulated: dict[str, Any] | None = None,
        _page_count: int = 0,
    ) -> dict[str, Any]:
        import asyncio

        if self._rate_limiter:
            await self._rate_limiter.async_wait(endpoint)

        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Authorization": self._token_manager.authorization,
        }
        if cont_yn:
            headers["cont_yn"] = cont_yn
        if cont_key:
            headers["cont_key"] = cont_key

        logger.debug("POST %s data=%s", endpoint, data)

        response = await self._client.post(endpoint, json=data, headers=headers)

        # Handle token expiry (IGW00121)
        if 500 <= response.status_code < 600:
            body = _safe_json(response)
            if isinstance(body, dict) and body.get("rsp_cd") == ERROR_TOKEN_EXPIRED:
                logger.info("Token expired (IGW00121), refreshing...")
                await asyncio.to_thread(self._token_manager.refresh)
                headers["Authorization"] = self._token_manager.authorization
                await asyncio.sleep(1.5)
                response = await self._client.post(endpoint, json=data, headers=headers)

        if response.status_code >= 400:
            body = _safe_json(response)
            rsp_cd = body.get("rsp_cd") if isinstance(body, dict) else None
            raise _classify_error(
                endpoint=endpoint,
                status_code=response.status_code,
                rsp_cd=rsp_cd,
                response_body=body,
                retry_after=response.headers.get("Retry-After"),
            )

        result: dict[str, Any] = response.json()

        # Merge pagination results into a single dict
        if paginate:
            merged = _merge_page(result, _accumulated)

            resp_cont_yn = response.headers.get("cont_yn", "N")
            resp_cont_key = response.headers.get("cont_key", "")

            if resp_cont_yn == "Y" and resp_cont_key and _page_count < _MAX_CONTINUATION:
                await asyncio.sleep(_CONTINUATION_DELAY)
                return await self._request_impl(
                    endpoint,
                    data,
                    paginate=True,
                    cont_yn=resp_cont_yn,
                    cont_key=resp_cont_key,
                    _accumulated=merged,
                    _page_count=_page_count + 1,
                )

            return merged

        return result


def _merge_page(new_page: dict[str, Any], accumulated: dict[str, Any] | None) -> dict[str, Any]:
    """Merge a new page into the accumulated result.

    List keys (Out1, Out2, Out3) are concatenated.
    Scalar keys (Out, rsp_cd, etc.) are overwritten with the latest page.
    """
    if accumulated is None:
        return dict(new_page)

    merged = dict(accumulated)
    for key, value in new_page.items():
        if key in _LIST_KEYS and isinstance(value, list):
            existing = merged.get(key, [])
            merged[key] = existing + value if isinstance(existing, list) else value
        else:
            merged[key] = value
    return merged


def _classify_error(
    *,
    endpoint: str,
    status_code: int,
    rsp_cd: str | None,
    response_body: dict[str, Any] | str | None,
    retry_after: str | None = None,
) -> APIError:
    """Classify an API error into the most specific exception type."""
    msg = f"API request failed: {endpoint} (HTTP {status_code})"
    kwargs: dict[str, Any] = dict(status_code=status_code, rsp_cd=rsp_cd, response_body=response_body)

    if status_code == 429:
        ra = float(retry_after) if retry_after else None
        return RateLimitError(msg, retry_after=ra, **kwargs)
    if rsp_cd and rsp_cd in ORDER_ERROR_CODES:
        return InvalidOrderError(msg, **kwargs)
    if rsp_cd and rsp_cd in BALANCE_ERROR_CODES:
        return InsufficientBalanceError(msg, **kwargs)
    if rsp_cd:
        logger.info(
            "Unclassified rsp_cd=%s on %s (HTTP %d)", rsp_cd, endpoint, status_code,
        )
    return APIError(msg, **kwargs)


def _safe_json(response: httpx.Response) -> dict[str, Any] | str:
    try:
        return response.json()  # type: ignore[no-any-return]
    except Exception:
        return response.text

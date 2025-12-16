"""Unified HTTP client helpers and factory (rc_cli internal)."""

from __future__ import annotations

import json
import logging
from typing import Any, Optional, Tuple

import httpx

logger = logging.getLogger(__name__)


class HTTPClientFactory:
    """Factory for creating standardized HTTP clients."""

    DEFAULT_MAX_KEEPALIVE = 10
    DEFAULT_MAX_CONNECTIONS = 20

    @staticmethod
    def create_sync_client(
        timeout: float = 30.0,
        auth: Optional[Tuple[str, str]] = None,
        follow_redirects: bool = True,
        headers: Optional[dict[str, str]] = None,
    ) -> httpx.Client:
        return httpx.Client(
            timeout=httpx.Timeout(timeout),
            auth=auth,
            follow_redirects=follow_redirects,
            headers=headers,
            limits=httpx.Limits(max_keepalive_connections=HTTPClientFactory.DEFAULT_MAX_KEEPALIVE),
        )

    @staticmethod
    def create_async_client(
        timeout: float = 30.0,
        auth: Optional[Tuple[str, str]] = None,
        follow_redirects: bool = True,
        headers: Optional[dict[str, str]] = None,
    ) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            auth=auth,
            follow_redirects=follow_redirects,
            headers=headers,
            limits=httpx.Limits(
                max_keepalive_connections=HTTPClientFactory.DEFAULT_MAX_KEEPALIVE,
                max_connections=HTTPClientFactory.DEFAULT_MAX_CONNECTIONS,
            ),
        )


def log_error(message: str, request_url: str | None = None, response_text: str | None = None) -> None:
    """Helper function to log formatted error messages."""
    error_msg = f"{message}"
    if request_url:
        error_msg += f" (URL: {request_url})"
    logger.error(error_msg)
    if response_text:
        truncated = response_text[:500] + "..." if len(response_text) > 500 else response_text
        logger.debug("Raw response: %s", truncated)


def make_sync_request(
    url: str,
    params: Optional[dict[str, Any]] = None,
    method: str = "GET",
    timeout: float = 30.0,
    auth: Optional[Tuple[str, str]] = None,
) -> Optional[dict[str, Any]]:
    """Make a synchronous HTTP request and handle common errors."""
    try:
        with HTTPClientFactory.create_sync_client(timeout=timeout, auth=auth) as client:
            m = method.upper()
            if m == "GET":
                response = client.get(url, params=params)
            elif m == "POST":
                response = client.post(url, json=params)
            elif m == "PUT":
                response = client.put(url, json=params)
            elif m == "DELETE":
                response = client.delete(url, params=params)
            else:
                log_error(f"Unsupported HTTP method: {method}", url)
                return None

            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        log_error(f"HTTP error {exc.response.status_code}", str(exc.request.url), exc.response.text)
    except httpx.RequestError as exc:
        request_url_for_error = str(exc.request.url) if getattr(exc, "request", None) else url
        log_error(f"Request error: {type(exc).__name__}", request_url_for_error)
    except json.JSONDecodeError:
        log_error("Failed to decode JSON response", url)
    return None


async def make_async_request(
    url: str,
    params: Optional[dict[str, Any]] = None,
    method: str = "GET",
    timeout: float = 30.0,
    auth: Optional[Tuple[str, str]] = None,
    headers: Optional[dict[str, str]] = None,
) -> Optional[dict[str, Any]]:
    """Make an async HTTP request and handle common errors."""
    try:
        async with HTTPClientFactory.create_async_client(timeout=timeout, auth=auth, headers=headers) as client:
            m = method.upper()
            if m == "GET":
                response = await client.get(url, params=params)
            elif m == "POST":
                response = await client.post(url, json=params)
            elif m == "PUT":
                response = await client.put(url, json=params)
            elif m == "DELETE":
                response = await client.delete(url, params=params)
            else:
                log_error(f"Unsupported HTTP method: {method}", url)
                return None

            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        log_error(f"HTTP error {exc.response.status_code}", str(exc.request.url), exc.response.text)
    except httpx.RequestError as exc:
        request_url_for_error = str(exc.request.url) if getattr(exc, "request", None) else url
        log_error(f"Request error: {type(exc).__name__}", request_url_for_error)
    except json.JSONDecodeError:
        log_error("Failed to decode JSON response", url)
    return None



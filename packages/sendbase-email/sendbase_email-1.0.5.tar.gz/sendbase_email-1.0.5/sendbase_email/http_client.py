"""HTTP client for SendBase API requests."""
from __future__ import annotations

from typing import Any, TypeVar

import httpx

from .exceptions import (
    SendBaseError,
    SendBaseAuthenticationError,
    SendBaseValidationError,
    SendBaseNotFoundError,
    SendBaseRateLimitError,
)

T = TypeVar("T")


class SendBaseHttpClient:
    """Internal HTTP client for making API requests."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.sendbase.app/api/v1",
        timeout: float = 30.0,
    ):
        self._client = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            headers={
                "X-API-Key": api_key,
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "sendbase-python/1.0.0",
            },
        )

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self) -> "SendBaseHttpClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def _handle_response(self, response: httpx.Response) -> Any:
        """Handle HTTP response and raise appropriate exceptions."""
        request_id = response.headers.get("X-Request-Id")

        if response.status_code == 204:
            return None

        if response.status_code >= 400:
            self._handle_error(response, request_id)

        if response.content:
            return response.json()
        return None

    def _handle_error(self, response: httpx.Response, request_id: str | None) -> None:
        """Handle error responses and raise appropriate exceptions."""
        error_data: dict[str, Any] = {}
        try:
            error_data = response.json() if response.content else {}
        except Exception:
            pass

        message = error_data.get("error") or error_data.get("message") or response.reason_phrase
        error_code = error_data.get("code")
        details = error_data.get("details")

        if response.status_code == 401:
            raise SendBaseAuthenticationError(
                message=message,
                error_code=error_code,
                request_id=request_id,
                details=details,
            )
        elif response.status_code == 400:
            errors = error_data.get("errors", {})
            raise SendBaseValidationError(
                message=message,
                errors=errors,
                error_code=error_code,
                request_id=request_id,
                details=details,
            )
        elif response.status_code == 404:
            raise SendBaseNotFoundError(
                message=message,
                error_code=error_code,
                request_id=request_id,
                details=details,
            )
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise SendBaseRateLimitError(
                message=message,
                retry_after=int(retry_after) if retry_after else None,
                error_code=error_code,
                request_id=request_id,
                details=details,
            )
        else:
            raise SendBaseError(
                message=message,
                status_code=response.status_code,
                error_code=error_code,
                request_id=request_id,
                details=details,
            )

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """Make a GET request."""
        response = self._client.get(path, params=params)
        return self._handle_response(response)

    def post(self, path: str, data: dict[str, Any] | None = None) -> Any:
        """Make a POST request."""
        response = self._client.post(path, json=data)
        return self._handle_response(response)

    def put(self, path: str, data: dict[str, Any] | None = None) -> Any:
        """Make a PUT request."""
        response = self._client.put(path, json=data)
        return self._handle_response(response)

    def patch(self, path: str, data: dict[str, Any] | None = None) -> Any:
        """Make a PATCH request."""
        response = self._client.patch(path, json=data)
        return self._handle_response(response)

    def delete(self, path: str) -> Any:
        """Make a DELETE request."""
        response = self._client.delete(path)
        return self._handle_response(response)


class AsyncSendBaseHttpClient:
    """Async HTTP client for making API requests."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.sendbase.app/api/v1",
        timeout: float = 30.0,
    ):
        self._client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
            headers={
                "X-API-Key": api_key,
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "sendbase-python/1.0.0",
            },
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> "AsyncSendBaseHttpClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    def _handle_response(self, response: httpx.Response) -> Any:
        """Handle HTTP response and raise appropriate exceptions."""
        request_id = response.headers.get("X-Request-Id")

        if response.status_code == 204:
            return None

        if response.status_code >= 400:
            self._handle_error(response, request_id)

        if response.content:
            return response.json()
        return None

    def _handle_error(self, response: httpx.Response, request_id: str | None) -> None:
        """Handle error responses and raise appropriate exceptions."""
        error_data: dict[str, Any] = {}
        try:
            error_data = response.json() if response.content else {}
        except Exception:
            pass

        message = error_data.get("error") or error_data.get("message") or response.reason_phrase
        error_code = error_data.get("code")
        details = error_data.get("details")

        if response.status_code == 401:
            raise SendBaseAuthenticationError(
                message=message,
                error_code=error_code,
                request_id=request_id,
                details=details,
            )
        elif response.status_code == 400:
            errors = error_data.get("errors", {})
            raise SendBaseValidationError(
                message=message,
                errors=errors,
                error_code=error_code,
                request_id=request_id,
                details=details,
            )
        elif response.status_code == 404:
            raise SendBaseNotFoundError(
                message=message,
                error_code=error_code,
                request_id=request_id,
                details=details,
            )
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise SendBaseRateLimitError(
                message=message,
                retry_after=int(retry_after) if retry_after else None,
                error_code=error_code,
                request_id=request_id,
                details=details,
            )
        else:
            raise SendBaseError(
                message=message,
                status_code=response.status_code,
                error_code=error_code,
                request_id=request_id,
                details=details,
            )

    async def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """Make a GET request."""
        response = await self._client.get(path, params=params)
        return self._handle_response(response)

    async def post(self, path: str, data: dict[str, Any] | None = None) -> Any:
        """Make a POST request."""
        response = await self._client.post(path, json=data)
        return self._handle_response(response)

    async def put(self, path: str, data: dict[str, Any] | None = None) -> Any:
        """Make a PUT request."""
        response = await self._client.put(path, json=data)
        return self._handle_response(response)

    async def patch(self, path: str, data: dict[str, Any] | None = None) -> Any:
        """Make a PATCH request."""
        response = await self._client.patch(path, json=data)
        return self._handle_response(response)

    async def delete(self, path: str) -> Any:
        """Make a DELETE request."""
        response = await self._client.delete(path)
        return self._handle_response(response)

"""Inbound client for SendBase API."""
from __future__ import annotations

from ..http_client import SendBaseHttpClient, AsyncSendBaseHttpClient
from ..models import InboundMessageResponse, InboundDownloadResponse


class InboundClient:
    """Client for inbound email operations."""

    def __init__(self, http: SendBaseHttpClient):
        self._http = http

    def list(
        self, page: int = 1, page_size: int = 50, domain_id: str | None = None
    ) -> list[InboundMessageResponse]:
        """List inbound emails."""
        params = {"page": page, "page_size": page_size}
        if domain_id:
            params["domain_id"] = domain_id
        response = self._http.get("inbound", params)
        # Server returns {"object": "list", "has_more": bool, "data": [...]}
        if isinstance(response, dict) and "data" in response:
            return [InboundMessageResponse.model_validate(item) for item in response["data"]]
        return [InboundMessageResponse.model_validate(item) for item in response]

    def get(self, inbound_id: str) -> InboundMessageResponse:
        """Get a specific inbound email by ID."""
        response = self._http.get(f"inbound/{inbound_id}")
        return InboundMessageResponse.model_validate(response)

    def get_raw(self, inbound_id: str) -> InboundDownloadResponse:
        """Get a signed URL to download the raw email."""
        response = self._http.get(f"inbound/{inbound_id}/raw")
        return InboundDownloadResponse.model_validate(response)

    def delete(self, inbound_id: str) -> None:
        """Delete an inbound email."""
        self._http.delete(f"inbound/{inbound_id}")


class AsyncInboundClient:
    """Async client for inbound email operations."""

    def __init__(self, http: AsyncSendBaseHttpClient):
        self._http = http

    async def list(
        self, page: int = 1, page_size: int = 50, domain_id: str | None = None
    ) -> list[InboundMessageResponse]:
        """List inbound emails."""
        params = {"page": page, "page_size": page_size}
        if domain_id:
            params["domain_id"] = domain_id
        response = await self._http.get("inbound", params)
        # Server returns {"object": "list", "has_more": bool, "data": [...]}
        if isinstance(response, dict) and "data" in response:
            return [InboundMessageResponse.model_validate(item) for item in response["data"]]
        return [InboundMessageResponse.model_validate(item) for item in response]

    async def get(self, inbound_id: str) -> InboundMessageResponse:
        """Get a specific inbound email by ID."""
        response = await self._http.get(f"inbound/{inbound_id}")
        return InboundMessageResponse.model_validate(response)

    async def get_raw(self, inbound_id: str) -> InboundDownloadResponse:
        """Get a signed URL to download the raw email."""
        response = await self._http.get(f"inbound/{inbound_id}/raw")
        return InboundDownloadResponse.model_validate(response)

    async def delete(self, inbound_id: str) -> None:
        """Delete an inbound email."""
        await self._http.delete(f"inbound/{inbound_id}")

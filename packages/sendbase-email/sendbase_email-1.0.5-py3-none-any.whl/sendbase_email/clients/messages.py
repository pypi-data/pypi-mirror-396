"""Messages client for SendBase API."""
from __future__ import annotations

from ..http_client import SendBaseHttpClient, AsyncSendBaseHttpClient
from ..models import MessageResponse


class MessagesClient:
    """Client for message operations."""

    def __init__(self, http: SendBaseHttpClient):
        self._http = http

    def list(self, page: int = 1, page_size: int = 50) -> list[MessageResponse]:
        """List messages."""
        params = {"page": page, "page_size": page_size}
        response = self._http.get("messages", params)
        return [MessageResponse.model_validate(item) for item in response]

    def get(self, message_id: str) -> MessageResponse:
        """Get a specific message by ID."""
        response = self._http.get(f"messages/{message_id}")
        return MessageResponse.model_validate(response)


class AsyncMessagesClient:
    """Async client for message operations."""

    def __init__(self, http: AsyncSendBaseHttpClient):
        self._http = http

    async def list(self, page: int = 1, page_size: int = 50) -> list[MessageResponse]:
        """List messages."""
        params = {"page": page, "page_size": page_size}
        response = await self._http.get("messages", params)
        return [MessageResponse.model_validate(item) for item in response]

    async def get(self, message_id: str) -> MessageResponse:
        """Get a specific message by ID."""
        response = await self._http.get(f"messages/{message_id}")
        return MessageResponse.model_validate(response)

"""Webhooks client for SendBase API."""
from __future__ import annotations

from ..http_client import SendBaseHttpClient, AsyncSendBaseHttpClient
from ..models import (
    CreateWebhookRequest,
    UpdateWebhookRequest,
    WebhookResponse,
    WebhookCreatedResponse,
    WebhookEventTypeResponse,
    WebhookDeliveryResponse,
    WebhookTestResponse,
)


class WebhooksClient:
    """Client for webhook operations."""

    def __init__(self, http: SendBaseHttpClient):
        self._http = http

    def create(self, request: CreateWebhookRequest) -> WebhookCreatedResponse:
        """Create a new webhook endpoint."""
        data = request.model_dump(by_alias=True, exclude_none=True)
        response = self._http.post("webhook-endpoints", data)
        return WebhookCreatedResponse.model_validate(response)

    def list(self) -> list[WebhookResponse]:
        """List all webhook endpoints."""
        response = self._http.get("webhook-endpoints")
        return [WebhookResponse.model_validate(item) for item in response]

    def get(self, webhook_id: str) -> WebhookResponse:
        """Get a specific webhook endpoint by ID."""
        response = self._http.get(f"webhook-endpoints/{webhook_id}")
        return WebhookResponse.model_validate(response)

    def update(self, webhook_id: str, request: UpdateWebhookRequest) -> WebhookResponse:
        """Update an existing webhook endpoint."""
        data = request.model_dump(by_alias=True, exclude_none=True)
        response = self._http.put(f"webhook-endpoints/{webhook_id}", data)
        return WebhookResponse.model_validate(response)

    def delete(self, webhook_id: str) -> None:
        """Delete a webhook endpoint."""
        self._http.delete(f"webhook-endpoints/{webhook_id}")

    def get_event_types(self) -> list[WebhookEventTypeResponse]:
        """Get available webhook event types."""
        response = self._http.get("webhook-endpoints/event-types")
        return [WebhookEventTypeResponse.model_validate(item) for item in response]

    def test(self, webhook_id: str) -> WebhookTestResponse:
        """Send a test event to a webhook endpoint."""
        response = self._http.post(f"webhook-endpoints/{webhook_id}/test")
        return WebhookTestResponse.model_validate(response)

    def get_deliveries(self, webhook_id: str, limit: int = 20) -> list[WebhookDeliveryResponse]:
        """Get recent deliveries for a webhook endpoint."""
        params = {"limit": limit}
        response = self._http.get(f"webhook-endpoints/{webhook_id}/deliveries", params)
        return [WebhookDeliveryResponse.model_validate(item) for item in response]


class AsyncWebhooksClient:
    """Async client for webhook operations."""

    def __init__(self, http: AsyncSendBaseHttpClient):
        self._http = http

    async def create(self, request: CreateWebhookRequest) -> WebhookCreatedResponse:
        """Create a new webhook endpoint."""
        data = request.model_dump(by_alias=True, exclude_none=True)
        response = await self._http.post("webhook-endpoints", data)
        return WebhookCreatedResponse.model_validate(response)

    async def list(self) -> list[WebhookResponse]:
        """List all webhook endpoints."""
        response = await self._http.get("webhook-endpoints")
        return [WebhookResponse.model_validate(item) for item in response]

    async def get(self, webhook_id: str) -> WebhookResponse:
        """Get a specific webhook endpoint by ID."""
        response = await self._http.get(f"webhook-endpoints/{webhook_id}")
        return WebhookResponse.model_validate(response)

    async def update(self, webhook_id: str, request: UpdateWebhookRequest) -> WebhookResponse:
        """Update an existing webhook endpoint."""
        data = request.model_dump(by_alias=True, exclude_none=True)
        response = await self._http.put(f"webhook-endpoints/{webhook_id}", data)
        return WebhookResponse.model_validate(response)

    async def delete(self, webhook_id: str) -> None:
        """Delete a webhook endpoint."""
        await self._http.delete(f"webhook-endpoints/{webhook_id}")

    async def get_event_types(self) -> list[WebhookEventTypeResponse]:
        """Get available webhook event types."""
        response = await self._http.get("webhook-endpoints/event-types")
        return [WebhookEventTypeResponse.model_validate(item) for item in response]

    async def test(self, webhook_id: str) -> WebhookTestResponse:
        """Send a test event to a webhook endpoint."""
        response = await self._http.post(f"webhook-endpoints/{webhook_id}/test")
        return WebhookTestResponse.model_validate(response)

    async def get_deliveries(
        self, webhook_id: str, limit: int = 20
    ) -> list[WebhookDeliveryResponse]:
        """Get recent deliveries for a webhook endpoint."""
        params = {"limit": limit}
        response = await self._http.get(f"webhook-endpoints/{webhook_id}/deliveries", params)
        return [WebhookDeliveryResponse.model_validate(item) for item in response]

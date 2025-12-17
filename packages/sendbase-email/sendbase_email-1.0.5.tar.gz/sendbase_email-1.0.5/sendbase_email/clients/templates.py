"""Templates client for SendBase API."""
from __future__ import annotations

from ..http_client import SendBaseHttpClient, AsyncSendBaseHttpClient
from ..models import (
    CreateTemplateRequest,
    UpdateTemplateRequest,
    TemplateResponse,
    TemplatePreviewResponse,
)


class TemplatesClient:
    """Client for template operations."""

    def __init__(self, http: SendBaseHttpClient):
        self._http = http

    def create(self, request: CreateTemplateRequest) -> TemplateResponse:
        """Create a new template."""
        data = request.model_dump(by_alias=True, exclude_none=True)
        response = self._http.post("templates", data)
        return TemplateResponse.model_validate(response)

    def list(self) -> list[TemplateResponse]:
        """List all templates."""
        response = self._http.get("templates")
        return [TemplateResponse.model_validate(item) for item in response]

    def get(self, template_id: str) -> TemplateResponse:
        """Get a specific template by ID."""
        response = self._http.get(f"templates/{template_id}")
        return TemplateResponse.model_validate(response)

    def update(self, template_id: str, request: UpdateTemplateRequest) -> TemplateResponse:
        """Update an existing template."""
        data = request.model_dump(by_alias=True, exclude_none=True)
        response = self._http.put(f"templates/{template_id}", data)
        return TemplateResponse.model_validate(response)

    def delete(self, template_id: str) -> None:
        """Delete a template."""
        self._http.delete(f"templates/{template_id}")

    def preview(
        self, template_id: str, variables: dict[str, str] | None = None
    ) -> TemplatePreviewResponse:
        """Preview a template with variables."""
        response = self._http.post(f"templates/{template_id}/preview", variables)
        return TemplatePreviewResponse.model_validate(response)


class AsyncTemplatesClient:
    """Async client for template operations."""

    def __init__(self, http: AsyncSendBaseHttpClient):
        self._http = http

    async def create(self, request: CreateTemplateRequest) -> TemplateResponse:
        """Create a new template."""
        data = request.model_dump(by_alias=True, exclude_none=True)
        response = await self._http.post("templates", data)
        return TemplateResponse.model_validate(response)

    async def list(self) -> list[TemplateResponse]:
        """List all templates."""
        response = await self._http.get("templates")
        return [TemplateResponse.model_validate(item) for item in response]

    async def get(self, template_id: str) -> TemplateResponse:
        """Get a specific template by ID."""
        response = await self._http.get(f"templates/{template_id}")
        return TemplateResponse.model_validate(response)

    async def update(self, template_id: str, request: UpdateTemplateRequest) -> TemplateResponse:
        """Update an existing template."""
        data = request.model_dump(by_alias=True, exclude_none=True)
        response = await self._http.put(f"templates/{template_id}", data)
        return TemplateResponse.model_validate(response)

    async def delete(self, template_id: str) -> None:
        """Delete a template."""
        await self._http.delete(f"templates/{template_id}")

    async def preview(
        self, template_id: str, variables: dict[str, str] | None = None
    ) -> TemplatePreviewResponse:
        """Preview a template with variables."""
        response = await self._http.post(f"templates/{template_id}/preview", variables)
        return TemplatePreviewResponse.model_validate(response)

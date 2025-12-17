"""Domains client for SendBase API."""
from __future__ import annotations

from ..http_client import SendBaseHttpClient, AsyncSendBaseHttpClient
from ..models import CreateDomainRequest, DomainResponse


class DomainsClient:
    """Client for domain operations."""

    def __init__(self, http: SendBaseHttpClient):
        self._http = http

    def create(self, request: CreateDomainRequest) -> DomainResponse:
        """Create a new domain."""
        data = request.model_dump(by_alias=True, exclude_none=True)
        response = self._http.post("domains", data)
        return DomainResponse.model_validate(response)

    def list(self) -> list[DomainResponse]:
        """List all domains."""
        response = self._http.get("domains")
        return [DomainResponse.model_validate(item) for item in response]

    def get(self, domain_id: str) -> DomainResponse:
        """Get a specific domain by ID."""
        response = self._http.get(f"domains/{domain_id}")
        return DomainResponse.model_validate(response)

    def verify(self, domain_id: str) -> DomainResponse:
        """Trigger verification for a domain."""
        response = self._http.get(f"domains/{domain_id}/verify")
        return DomainResponse.model_validate(response)

    def delete(self, domain_id: str) -> None:
        """Delete a domain."""
        self._http.delete(f"domains/{domain_id}")

    def enable_inbound(self, domain_id: str) -> None:
        """Enable inbound email for a domain."""
        self._http.post(f"domains/{domain_id}/inbound/enable")

    def disable_inbound(self, domain_id: str) -> None:
        """Disable inbound email for a domain."""
        self._http.post(f"domains/{domain_id}/inbound/disable")


class AsyncDomainsClient:
    """Async client for domain operations."""

    def __init__(self, http: AsyncSendBaseHttpClient):
        self._http = http

    async def create(self, request: CreateDomainRequest) -> DomainResponse:
        """Create a new domain."""
        data = request.model_dump(by_alias=True, exclude_none=True)
        response = await self._http.post("domains", data)
        return DomainResponse.model_validate(response)

    async def list(self) -> list[DomainResponse]:
        """List all domains."""
        response = await self._http.get("domains")
        return [DomainResponse.model_validate(item) for item in response]

    async def get(self, domain_id: str) -> DomainResponse:
        """Get a specific domain by ID."""
        response = await self._http.get(f"domains/{domain_id}")
        return DomainResponse.model_validate(response)

    async def verify(self, domain_id: str) -> DomainResponse:
        """Trigger verification for a domain."""
        response = await self._http.get(f"domains/{domain_id}/verify")
        return DomainResponse.model_validate(response)

    async def delete(self, domain_id: str) -> None:
        """Delete a domain."""
        await self._http.delete(f"domains/{domain_id}")

    async def enable_inbound(self, domain_id: str) -> None:
        """Enable inbound email for a domain."""
        await self._http.post(f"domains/{domain_id}/inbound/enable")

    async def disable_inbound(self, domain_id: str) -> None:
        """Disable inbound email for a domain."""
        await self._http.post(f"domains/{domain_id}/inbound/disable")

"""Tenants client for SendBase API."""
from __future__ import annotations

from ..http_client import SendBaseHttpClient, AsyncSendBaseHttpClient
from ..models import CurrentTenantResponse


class TenantsClient:
    """Client for tenant operations.

    Note: Most tenant operations (create, list, update, delete, members, invitations)
    require Bearer token authentication and are not available via API key.
    Only get_current() works with API key auth.
    """

    def __init__(self, http: SendBaseHttpClient):
        self._http = http

    def get_current(self) -> CurrentTenantResponse:
        """Get the current tenant (works with API key auth).

        Returns info about the tenant associated with the current API key.
        """
        response = self._http.get("tenant")
        return CurrentTenantResponse.model_validate(response)


class AsyncTenantsClient:
    """Async client for tenant operations.

    Note: Most tenant operations (create, list, update, delete, members, invitations)
    require Bearer token authentication and are not available via API key.
    Only get_current() works with API key auth.
    """

    def __init__(self, http: AsyncSendBaseHttpClient):
        self._http = http

    async def get_current(self) -> CurrentTenantResponse:
        """Get the current tenant (works with API key auth).

        Returns info about the tenant associated with the current API key.
        """
        response = await self._http.get("tenant")
        return CurrentTenantResponse.model_validate(response)

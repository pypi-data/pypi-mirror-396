"""SendBase Email SDK client."""
from __future__ import annotations

from .http_client import SendBaseHttpClient, AsyncSendBaseHttpClient
from .clients import (
    EmailsClient,
    AsyncEmailsClient,
    DomainsClient,
    AsyncDomainsClient,
    TemplatesClient,
    AsyncTemplatesClient,
    MessagesClient,
    AsyncMessagesClient,
    InboundClient,
    AsyncInboundClient,
    WebhooksClient,
    AsyncWebhooksClient,
    BillingClient,
    AsyncBillingClient,
    TenantsClient,
    AsyncTenantsClient,
)


class SendBaseClient:
    """
    SendBase Email API client.

    Example usage:
        ```python
        from sendbase_email import SendBaseClient, SendEmailRequest

        client = SendBaseClient("your-api-key")

        # Send an email
        response = client.emails.send(SendEmailRequest(
            from_email="sender@yourdomain.com",
            to=["recipient@example.com"],
            subject="Hello!",
            html_body="<h1>Welcome!</h1>"
        ))
        print(f"Message ID: {response.message_id}")

        # Use as context manager
        with SendBaseClient("your-api-key") as client:
            domains = client.domains.list()
        ```
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.sendbase.app/api/v1",
        timeout: float = 30.0,
    ):
        """
        Initialize the SendBase client.

        Args:
            api_key: Your SendBase API key.
            base_url: The base URL for the API (default: https://api.sendbase.app/api/v1).
            timeout: Request timeout in seconds (default: 30).
        """
        self._http = SendBaseHttpClient(api_key, base_url, timeout)

        # Initialize sub-clients
        self._emails = EmailsClient(self._http)
        self._domains = DomainsClient(self._http)
        self._templates = TemplatesClient(self._http)
        self._messages = MessagesClient(self._http)
        self._inbound = InboundClient(self._http)
        self._webhooks = WebhooksClient(self._http)
        self._billing = BillingClient(self._http)
        self._tenants = TenantsClient(self._http)

    @property
    def emails(self) -> EmailsClient:
        """Email operations."""
        return self._emails

    @property
    def domains(self) -> DomainsClient:
        """Domain operations."""
        return self._domains

    @property
    def templates(self) -> TemplatesClient:
        """Template operations."""
        return self._templates

    @property
    def messages(self) -> MessagesClient:
        """Message operations."""
        return self._messages

    @property
    def inbound(self) -> InboundClient:
        """Inbound email operations."""
        return self._inbound

    @property
    def webhooks(self) -> WebhooksClient:
        """Webhook operations."""
        return self._webhooks

    @property
    def billing(self) -> BillingClient:
        """Billing operations."""
        return self._billing

    @property
    def tenants(self) -> TenantsClient:
        """Tenant operations (get_current only - other operations require Bearer auth)."""
        return self._tenants

    def close(self) -> None:
        """Close the client and release resources."""
        self._http.close()

    def __enter__(self) -> "SendBaseClient":
        return self

    def __exit__(self, *args) -> None:
        self.close()


class AsyncSendBaseClient:
    """
    Async SendBase Email API client.

    Example usage:
        ```python
        import asyncio
        from sendbase_email import AsyncSendBaseClient, SendEmailRequest

        async def main():
            async with AsyncSendBaseClient("your-api-key") as client:
                response = await client.emails.send(SendEmailRequest(
                    from_email="sender@yourdomain.com",
                    to=["recipient@example.com"],
                    subject="Hello!",
                    html_body="<h1>Welcome!</h1>"
                ))
                print(f"Message ID: {response.message_id}")

        asyncio.run(main())
        ```
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.sendbase.app/api/v1",
        timeout: float = 30.0,
    ):
        """
        Initialize the async SendBase client.

        Args:
            api_key: Your SendBase API key.
            base_url: The base URL for the API (default: https://api.sendbase.app/api/v1).
            timeout: Request timeout in seconds (default: 30).
        """
        self._http = AsyncSendBaseHttpClient(api_key, base_url, timeout)

        # Initialize sub-clients
        self._emails = AsyncEmailsClient(self._http)
        self._domains = AsyncDomainsClient(self._http)
        self._templates = AsyncTemplatesClient(self._http)
        self._messages = AsyncMessagesClient(self._http)
        self._inbound = AsyncInboundClient(self._http)
        self._webhooks = AsyncWebhooksClient(self._http)
        self._billing = AsyncBillingClient(self._http)
        self._tenants = AsyncTenantsClient(self._http)

    @property
    def emails(self) -> AsyncEmailsClient:
        """Email operations."""
        return self._emails

    @property
    def domains(self) -> AsyncDomainsClient:
        """Domain operations."""
        return self._domains

    @property
    def templates(self) -> AsyncTemplatesClient:
        """Template operations."""
        return self._templates

    @property
    def messages(self) -> AsyncMessagesClient:
        """Message operations."""
        return self._messages

    @property
    def inbound(self) -> AsyncInboundClient:
        """Inbound email operations."""
        return self._inbound

    @property
    def webhooks(self) -> AsyncWebhooksClient:
        """Webhook operations."""
        return self._webhooks

    @property
    def billing(self) -> AsyncBillingClient:
        """Billing operations."""
        return self._billing

    @property
    def tenants(self) -> AsyncTenantsClient:
        """Tenant operations (get_current only - other operations require Bearer auth)."""
        return self._tenants

    async def close(self) -> None:
        """Close the client and release resources."""
        await self._http.close()

    async def __aenter__(self) -> "AsyncSendBaseClient":
        return self

    async def __aexit__(self, *args) -> None:
        await self.close()

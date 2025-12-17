"""Emails client for SendBase API."""
from __future__ import annotations

from typing import Any

from ..http_client import SendBaseHttpClient, AsyncSendBaseHttpClient
from ..models import (
    SendEmailRequest,
    SendEmailResponse,
    BatchEmailResponse,
    MessageResponse,
)


class EmailsClient:
    """Client for email operations."""

    def __init__(self, http: SendBaseHttpClient):
        self._http = http

    def send(self, request: SendEmailRequest) -> SendEmailResponse:
        """Send a single email."""
        data = request.model_dump(by_alias=True, exclude_none=True)
        # Convert recipients to proper format
        if "to" in data:
            data["to"] = self._format_recipients(data["to"])
        if "cc" in data:
            data["cc"] = self._format_recipients(data["cc"])
        if "bcc" in data:
            data["bcc"] = self._format_recipients(data["bcc"])
        response = self._http.post("emails/send", data)
        return SendEmailResponse.model_validate(response)

    def send_batch(self, requests: list[SendEmailRequest]) -> BatchEmailResponse:
        """Send multiple emails in a batch."""
        emails = []
        for r in requests:
            email_data = r.model_dump(by_alias=True, exclude_none=True)
            # Format recipients like send() does
            if "to" in email_data:
                email_data["to"] = self._format_recipients(email_data["to"])
            if "cc" in email_data:
                email_data["cc"] = self._format_recipients(email_data["cc"])
            if "bcc" in email_data:
                email_data["bcc"] = self._format_recipients(email_data["bcc"])
            emails.append(email_data)
        response = self._http.post("emails/batch", {"emails": emails})
        return BatchEmailResponse.model_validate(response)

    def list(
        self,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
        from_email: str | None = None,
        to_email: str | None = None,
    ) -> list[MessageResponse]:
        """List emails with optional filters."""
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        if status:
            params["status"] = status
        if from_email:
            params["from_email"] = from_email
        if to_email:
            params["to_email"] = to_email
        response = self._http.get("emails", params)
        if isinstance(response, dict) and "items" in response:
            return [MessageResponse.model_validate(item) for item in response["items"]]
        return [MessageResponse.model_validate(item) for item in response]

    def get(self, message_id: str) -> MessageResponse:
        """Get a specific email by ID."""
        response = self._http.get(f"emails/{message_id}")
        return MessageResponse.model_validate(response)

    def cancel(self, message_id: str) -> None:
        """Cancel a scheduled email."""
        self._http.post(f"emails/{message_id}/cancel")

    def _format_recipients(self, recipients: list[Any]) -> list[dict[str, str]]:
        """Format recipients for API request. Converts strings to {email: ...} objects."""
        result = []
        for r in recipients:
            if isinstance(r, str):
                result.append({"email": r})  # Server requires {email: "..."} objects
            elif isinstance(r, dict):
                result.append(r)
            else:
                result.append(r.model_dump(by_alias=True, exclude_none=True))
        return result


class AsyncEmailsClient:
    """Async client for email operations."""

    def __init__(self, http: AsyncSendBaseHttpClient):
        self._http = http

    async def send(self, request: SendEmailRequest) -> SendEmailResponse:
        """Send a single email."""
        data = request.model_dump(by_alias=True, exclude_none=True)
        if "to" in data:
            data["to"] = self._format_recipients(data["to"])
        if "cc" in data:
            data["cc"] = self._format_recipients(data["cc"])
        if "bcc" in data:
            data["bcc"] = self._format_recipients(data["bcc"])
        response = await self._http.post("emails/send", data)
        return SendEmailResponse.model_validate(response)

    async def send_batch(self, requests: list[SendEmailRequest]) -> BatchEmailResponse:
        """Send multiple emails in a batch."""
        emails = []
        for r in requests:
            email_data = r.model_dump(by_alias=True, exclude_none=True)
            # Format recipients like send() does
            if "to" in email_data:
                email_data["to"] = self._format_recipients(email_data["to"])
            if "cc" in email_data:
                email_data["cc"] = self._format_recipients(email_data["cc"])
            if "bcc" in email_data:
                email_data["bcc"] = self._format_recipients(email_data["bcc"])
            emails.append(email_data)
        response = await self._http.post("emails/batch", {"emails": emails})
        return BatchEmailResponse.model_validate(response)

    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
        from_email: str | None = None,
        to_email: str | None = None,
    ) -> list[MessageResponse]:
        """List emails with optional filters."""
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        if status:
            params["status"] = status
        if from_email:
            params["from_email"] = from_email
        if to_email:
            params["to_email"] = to_email
        response = await self._http.get("emails", params)
        if isinstance(response, dict) and "items" in response:
            return [MessageResponse.model_validate(item) for item in response["items"]]
        return [MessageResponse.model_validate(item) for item in response]

    async def get(self, message_id: str) -> MessageResponse:
        """Get a specific email by ID."""
        response = await self._http.get(f"emails/{message_id}")
        return MessageResponse.model_validate(response)

    async def cancel(self, message_id: str) -> None:
        """Cancel a scheduled email."""
        await self._http.post(f"emails/{message_id}/cancel")

    def _format_recipients(self, recipients: list[Any]) -> list[dict[str, str]]:
        """Format recipients for API request. Converts strings to {email: ...} objects."""
        result = []
        for r in recipients:
            if isinstance(r, str):
                result.append({"email": r})  # Server requires {email: "..."} objects
            elif isinstance(r, dict):
                result.append(r)
            else:
                result.append(r.model_dump(by_alias=True, exclude_none=True))
        return result

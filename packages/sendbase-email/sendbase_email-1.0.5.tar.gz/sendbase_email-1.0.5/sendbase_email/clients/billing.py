"""Billing client for SendBase API."""
from __future__ import annotations

from ..http_client import SendBaseHttpClient, AsyncSendBaseHttpClient
from ..models import (
    PlanResponse,
    SubscriptionResponse,
    UsageResponse,
    UsageSummaryResponse,
    LimitsResponse,
    CheckoutResponse,
    PortalResponse,
    InvoiceResponse,
)


class BillingClient:
    """Client for billing operations."""

    def __init__(self, http: SendBaseHttpClient):
        self._http = http

    def get_plans(self) -> list[PlanResponse]:
        """Get available billing plans."""
        response = self._http.get("billing/plans")
        return [PlanResponse.model_validate(item) for item in response]

    def get_subscription(self) -> SubscriptionResponse:
        """Get current subscription."""
        response = self._http.get("billing/subscription")
        return SubscriptionResponse.model_validate(response)

    def create_checkout(self, plan_id: str) -> CheckoutResponse:
        """Create a checkout session for a plan."""
        response = self._http.post("billing/checkout", {"planId": plan_id})
        return CheckoutResponse.model_validate(response)

    def create_portal_session(self) -> PortalResponse:
        """Create a billing portal session."""
        response = self._http.post("billing/portal", {})
        return PortalResponse.model_validate(response)

    def update_plan(self, plan_id: str) -> SubscriptionResponse:
        """Update subscription to a different plan."""
        response = self._http.put("billing/subscription/plan", {"planId": plan_id})
        return SubscriptionResponse.model_validate(response)

    def cancel_subscription(self) -> None:
        """Cancel the current subscription."""
        self._http.post("billing/subscription/cancel")

    def reactivate_subscription(self) -> None:
        """Reactivate a cancelled subscription."""
        self._http.post("billing/subscription/reactivate")

    def get_usage(self) -> UsageResponse:
        """Get current usage statistics."""
        response = self._http.get("billing/usage")
        return UsageResponse.model_validate(response)

    def get_usage_history(self, months: int = 6) -> list[UsageSummaryResponse]:
        """Get usage history."""
        params = {"months": months}
        response = self._http.get("billing/usage/history", params)
        return [UsageSummaryResponse.model_validate(item) for item in response]

    def get_invoices(self) -> list[InvoiceResponse]:
        """Get invoices."""
        response = self._http.get("billing/invoices")
        return [InvoiceResponse.model_validate(item) for item in response]

    def get_limits(self) -> LimitsResponse:
        """Get account limits."""
        response = self._http.get("billing/limits")
        return LimitsResponse.model_validate(response)


class AsyncBillingClient:
    """Async client for billing operations."""

    def __init__(self, http: AsyncSendBaseHttpClient):
        self._http = http

    async def get_plans(self) -> list[PlanResponse]:
        """Get available billing plans."""
        response = await self._http.get("billing/plans")
        return [PlanResponse.model_validate(item) for item in response]

    async def get_subscription(self) -> SubscriptionResponse:
        """Get current subscription."""
        response = await self._http.get("billing/subscription")
        return SubscriptionResponse.model_validate(response)

    async def create_checkout(self, plan_id: str) -> CheckoutResponse:
        """Create a checkout session for a plan."""
        response = await self._http.post("billing/checkout", {"planId": plan_id})
        return CheckoutResponse.model_validate(response)

    async def create_portal_session(self) -> PortalResponse:
        """Create a billing portal session."""
        response = await self._http.post("billing/portal", {})
        return PortalResponse.model_validate(response)

    async def update_plan(self, plan_id: str) -> SubscriptionResponse:
        """Update subscription to a different plan."""
        response = await self._http.put("billing/subscription/plan", {"planId": plan_id})
        return SubscriptionResponse.model_validate(response)

    async def cancel_subscription(self) -> None:
        """Cancel the current subscription."""
        await self._http.post("billing/subscription/cancel")

    async def reactivate_subscription(self) -> None:
        """Reactivate a cancelled subscription."""
        await self._http.post("billing/subscription/reactivate")

    async def get_usage(self) -> UsageResponse:
        """Get current usage statistics."""
        response = await self._http.get("billing/usage")
        return UsageResponse.model_validate(response)

    async def get_usage_history(self, months: int = 6) -> list[UsageSummaryResponse]:
        """Get usage history."""
        params = {"months": months}
        response = await self._http.get("billing/usage/history", params)
        return [UsageSummaryResponse.model_validate(item) for item in response]

    async def get_invoices(self) -> list[InvoiceResponse]:
        """Get invoices."""
        response = await self._http.get("billing/invoices")
        return [InvoiceResponse.model_validate(item) for item in response]

    async def get_limits(self) -> LimitsResponse:
        """Get account limits."""
        response = await self._http.get("billing/limits")
        return LimitsResponse.model_validate(response)

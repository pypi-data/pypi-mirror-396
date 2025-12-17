"""SendBase SDK data models - mapped directly to server DTOs."""
from __future__ import annotations

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field, ConfigDict


class BaseModelConfig(BaseModel):
    """Base model configuration."""

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        extra="ignore",
    )


# =============================================================================
# Email Models (Server uses snake_case via [JsonPropertyName])
# =============================================================================


class EmailRecipient(BaseModelConfig):
    """Email recipient with optional name."""
    email: str
    name: str | None = None


class EmailAttachment(BaseModelConfig):
    """Email attachment."""
    filename: str
    content: str | None = None
    content_type: str | None = None
    path: str | None = None


class SendEmailRequest(BaseModelConfig):
    """Request to send an email - matches Email.Server.DTOs.Requests.SendEmailRequest."""
    from_email: str
    from_name: str | None = None
    to: list[str | EmailRecipient]
    cc: list[str | EmailRecipient] | None = None
    bcc: list[str | EmailRecipient] | None = None
    subject: str
    html_body: str | None = None
    text_body: str | None = None
    tags: dict[str, str] | None = None
    template_id: str | None = None
    template_variables: dict[str, str] | None = None
    scheduled_at_utc: datetime | None = None
    attachments: list[EmailAttachment] | None = None


class SendEmailResponse(BaseModelConfig):
    """Response from sending - matches Email.Server.DTOs.Responses.SendEmailResponse."""
    message_id: str
    status: int
    status_text: str
    ses_message_id: str | None = None


class BatchEmailItemResult(BaseModelConfig):
    """Individual result in batch send response."""
    index: int
    success: bool
    message_id: str | None = None
    error: str | None = None


class BatchEmailResponse(BaseModelConfig):
    """Batch send response - matches Email.Server.DTOs.Responses.BatchEmailResponse."""
    batch_id: str
    total: int
    succeeded: int
    failed: int
    results: list[BatchEmailItemResult]


class RecipientResponse(BaseModelConfig):
    """Recipient in message response."""
    id: int | None = None
    email: str
    name: str | None = None
    kind: int
    kind_text: str
    delivery_status: int
    delivery_status_text: str
    ses_delivery_id: str | None = None


class MessageEventResponse(BaseModelConfig):
    """Event in message response."""
    id: int
    event_type: str
    occurred_at_utc: datetime
    recipient: str | None = None


class MessageResponse(BaseModelConfig):
    """Full message - matches Email.Server.DTOs.Responses.MessageResponse (snake_case)."""
    id: str
    from_email: str
    from_name: str | None = None
    subject: str | None = None
    status: int
    status_text: str
    ses_message_id: str | None = None
    scheduled_at_utc: datetime | None = None
    requested_at_utc: datetime | None = None
    sent_at_utc: datetime | None = None
    error: str | None = None
    recipients: list[RecipientResponse] | None = None
    events: list[MessageEventResponse] | None = None
    tags: dict[str, str] | None = None


# =============================================================================
# Domain Models (Server uses snake_case via [JsonPropertyName])
# Note: Server uses "domain" not "domain_name"
# =============================================================================


class CreateDomainRequest(BaseModelConfig):
    """Request to create domain."""
    domain_name: str
    region: str | None = None


class DnsRecordResponse(BaseModelConfig):
    """DNS record - matches Email.Server.DTOs.Responses.DnsRecordResponse (snake_case)."""
    id: int
    record_type: str
    host: str
    value: str
    required: bool
    last_checked_utc: datetime | None = None
    status: int
    status_text: str


class DomainResponse(BaseModelConfig):
    """Domain - matches Email.Server.DTOs.Responses.DomainResponse (snake_case).
    Note: Server uses 'domain' not 'domain_name'.
    """
    id: str
    domain: str  # Server uses "domain" not "domain_name"
    region: str
    verification_status: int
    verification_status_text: str
    dkim_status: int
    dkim_status_text: str
    mail_from_status: int | None = None
    mail_from_subdomain: str | None = None
    identity_arn: str | None = None
    created_at_utc: datetime | None = None
    verified_at_utc: datetime | None = None
    inbound_enabled: bool | None = None
    inbound_status: int
    inbound_status_text: str
    dns_records: list[DnsRecordResponse] | None = None


# =============================================================================
# Template Models (Server uses snake_case via [JsonPropertyName])
# =============================================================================


class CreateTemplateRequest(BaseModelConfig):
    """Request to create template - matches server (snake_case)."""
    name: str
    subject: str
    html_body: str | None = None
    text_body: str | None = None


class UpdateTemplateRequest(BaseModelConfig):
    """Request to update template."""
    name: str | None = None
    subject: str | None = None
    html_body: str | None = None
    text_body: str | None = None


class TemplateResponse(BaseModelConfig):
    """Template - matches Email.Server.DTOs.Responses.TemplateResponse (snake_case)."""
    id: str
    name: str
    version: int | None = None
    subject: str | None = None
    html_body: str | None = None
    text_body: str | None = None
    variables: list[str] | None = None
    created_at_utc: datetime | None = None


class TemplatePreviewResponse(BaseModelConfig):
    """Template preview result - RenderedTemplate uses camelCase (no JsonPropertyName)."""
    subject: str | None = Field(default=None, alias="subject")
    html_body: str | None = Field(default=None, alias="htmlBody")
    text_body: str | None = Field(default=None, alias="textBody")

    model_config = ConfigDict(populate_by_name=True)


# =============================================================================
# API Key Models (Server uses snake_case via [JsonPropertyName])
# =============================================================================


class CreateApiKeyRequest(BaseModelConfig):
    """Request to create API key."""
    name: str
    scopes: list[str] | None = None
    expires_at: datetime | None = None


class ApiKeyResponse(BaseModelConfig):
    """API key (without actual key)."""
    id: str
    name: str
    key_prefix: str
    scopes: list[str] | None = None
    created_at: datetime | None = None
    expires_at: datetime | None = None
    last_used_at: datetime | None = None


class ApiKeyCreatedResponse(BaseModelConfig):
    """API key creation response (includes actual key)."""
    id: str
    name: str
    key: str
    key_prefix: str
    scopes: list[str] | None = None
    created_at: datetime | None = None
    expires_at: datetime | None = None


class ApiKeyScopesResponse(BaseModelConfig):
    """Available scopes."""
    scopes: list[str]


# =============================================================================
# Webhook Models (Server uses camelCase - NO [JsonPropertyName])
# =============================================================================


class CreateWebhookRequest(BaseModelConfig):
    """Request to create webhook - matches server (camelCase, no JsonPropertyName)."""
    name: str = Field(..., alias="name")
    url: str = Field(..., alias="url")
    event_types: list[str] = Field(..., alias="eventTypes")

    model_config = ConfigDict(populate_by_name=True)


class UpdateWebhookRequest(BaseModelConfig):
    """Request to update webhook (camelCase)."""
    name: str | None = Field(default=None, alias="name")
    url: str | None = Field(default=None, alias="url")
    event_types: list[str] | None = Field(default=None, alias="eventTypes")
    enabled: bool | None = Field(default=None, alias="enabled")

    model_config = ConfigDict(populate_by_name=True)


class WebhookResponse(BaseModelConfig):
    """Webhook - matches WebhookEndpointResponse (camelCase, no JsonPropertyName)."""
    id: str = Field(..., alias="id")
    name: str = Field(..., alias="name")
    url: str = Field(..., alias="url")
    event_types: list[str] = Field(..., alias="eventTypes")
    enabled: bool = Field(..., alias="enabled")
    secret_preview: str | None = Field(default=None, alias="secretPreview")
    created_at_utc: datetime | None = Field(default=None, alias="createdAtUtc")

    model_config = ConfigDict(populate_by_name=True)


class WebhookCreatedResponse(BaseModelConfig):
    """Webhook creation response."""
    endpoint: WebhookResponse
    secret: str


class WebhookEventTypeResponse(BaseModelConfig):
    """Webhook event type (camelCase)."""
    name: str = Field(..., alias="name")
    description: str = Field(..., alias="description")

    model_config = ConfigDict(populate_by_name=True)


class WebhookDeliveryResponse(BaseModelConfig):
    """Webhook delivery (camelCase)."""
    id: str = Field(..., alias="id")
    event_type: str = Field(..., alias="eventType")
    status_code: int | None = Field(default=None, alias="statusCode")
    success: bool = Field(..., alias="success")
    attempted_at: datetime | None = Field(default=None, alias="attemptedAt")
    response_body: str | None = Field(default=None, alias="responseBody")

    model_config = ConfigDict(populate_by_name=True)


class WebhookTestResponse(BaseModelConfig):
    """Webhook test result (camelCase)."""
    success: bool = Field(..., alias="success")
    status_code: int | None = Field(default=None, alias="statusCode")
    response_body: str | None = Field(default=None, alias="responseBody")
    error: str | None = Field(default=None, alias="error")

    model_config = ConfigDict(populate_by_name=True)


# =============================================================================
# Inbound Models (Check server for actual format)
# =============================================================================


class InboundAttachmentResponse(BaseModelConfig):
    """Inbound email attachment - matches server (snake_case with JsonPropertyName)."""
    id: str
    filename: str
    content_type: str
    content_id: str | None = None
    content_disposition: str = "attachment"
    size: int


class InboundMessageResponse(BaseModelConfig):
    """Inbound email message - matches server InboundMessageResponse (snake_case)."""
    id: str
    to: list[str] = []
    from_: str = Field(..., alias="from")  # "from" is reserved keyword
    created_at: datetime
    subject: str | None = None
    bcc: list[str] = []
    cc: list[str] = []
    reply_to: list[str] = []
    message_id: str | None = None
    attachments: list[InboundAttachmentResponse] = []

    model_config = ConfigDict(populate_by_name=True)


class InboundDownloadResponse(BaseModelConfig):
    """Inbound email download URL - matches server InboundEmailDownloadResponse (snake_case)."""
    download_url: str
    expires_at_utc: datetime


# =============================================================================
# Billing Models (Server uses camelCase - NO [JsonPropertyName])
# =============================================================================


class PlanResponse(BaseModelConfig):
    """Billing plan - matches BillingPlanResponse (camelCase, no JsonPropertyName)."""
    id: str = Field(..., alias="id")
    name: str = Field(..., alias="name")
    display_name: str = Field(..., alias="displayName")
    monthly_price_cents: int = Field(..., alias="monthlyPriceCents")
    included_emails: int = Field(..., alias="includedEmails")
    overage_rate_cents_per_1k: int = Field(..., alias="overageRateCentsPer1K")
    allows_overage: bool = Field(..., alias="allowsOverage")
    max_api_keys: int = Field(..., alias="maxApiKeys")
    max_domains: int = Field(..., alias="maxDomains")
    max_team_members: int = Field(..., alias="maxTeamMembers")
    max_webhooks: int = Field(..., alias="maxWebhooks")
    max_templates: int = Field(..., alias="maxTemplates")
    analytics_retention_days: int = Field(..., alias="analyticsRetentionDays")
    has_dedicated_ip: bool = Field(..., alias="hasDedicatedIp")
    support_level: str = Field(..., alias="supportLevel")
    stripe_payment_link_url: str | None = Field(default=None, alias="stripePaymentLinkUrl")

    model_config = ConfigDict(populate_by_name=True)


class SubscriptionResponse(BaseModelConfig):
    """Subscription (camelCase)."""
    plan_id: str | None = Field(default=None, alias="planId")
    plan_name: str | None = Field(default=None, alias="planName")
    status: str | None = Field(default=None, alias="status")
    current_period_start: datetime | None = Field(default=None, alias="currentPeriodStart")
    current_period_end: datetime | None = Field(default=None, alias="currentPeriodEnd")
    cancel_at_period_end: bool = Field(default=False, alias="cancelAtPeriodEnd")

    model_config = ConfigDict(populate_by_name=True)


class UsageResponse(BaseModelConfig):
    """Usage - matches UsageSummaryResponse (camelCase)."""
    period_id: str | None = Field(default=None, alias="periodId")
    current_period_start: datetime | None = Field(default=None, alias="currentPeriodStart")
    current_period_end: datetime | None = Field(default=None, alias="currentPeriodEnd")
    emails_sent: int = Field(default=0, alias="emailsSent")
    emails_included: int = Field(default=0, alias="emailsIncluded")
    emails_remaining: int = Field(default=0, alias="emailsRemaining")
    overage_emails: int = Field(default=0, alias="overageEmails")
    usage_percentage: float = Field(default=0.0, alias="usagePercentage")
    estimated_overage_cost_cents: int = Field(default=0, alias="estimatedOverageCostCents")
    days_remaining_in_period: int = Field(default=0, alias="daysRemainingInPeriod")
    is_current_period: bool = Field(default=False, alias="isCurrentPeriod")

    model_config = ConfigDict(populate_by_name=True)


class UsageSummaryResponse(BaseModelConfig):
    """Usage summary (camelCase)."""
    period_id: str = Field(..., alias="periodId")
    current_period_start: datetime = Field(..., alias="currentPeriodStart")
    current_period_end: datetime = Field(..., alias="currentPeriodEnd")
    emails_sent: int = Field(..., alias="emailsSent")
    emails_included: int = Field(..., alias="emailsIncluded")
    emails_remaining: int = Field(..., alias="emailsRemaining")
    overage_emails: int = Field(..., alias="overageEmails")
    usage_percentage: float = Field(..., alias="usagePercentage")
    estimated_overage_cost_cents: int = Field(..., alias="estimatedOverageCostCents")
    days_remaining_in_period: int = Field(..., alias="daysRemainingInPeriod")
    is_current_period: bool = Field(..., alias="isCurrentPeriod")

    model_config = ConfigDict(populate_by_name=True)


class LimitsResponse(BaseModelConfig):
    """Limits - matches PlanLimitsResponse (camelCase)."""
    plan_name: str | None = Field(default=None, alias="planName")
    emails_included: int | None = Field(default=None, alias="emailsIncluded")
    max_domains: int | None = Field(default=None, alias="maxDomains")
    max_api_keys: int | None = Field(default=None, alias="maxApiKeys")
    max_webhooks: int | None = Field(default=None, alias="maxWebhooks")
    overage_rate_cents_per_1k: int | None = Field(default=None, alias="overageRateCentsPer1K")

    model_config = ConfigDict(populate_by_name=True)


class CheckoutResponse(BaseModelConfig):
    """Checkout session (camelCase)."""
    url: str = Field(..., alias="url")
    session_id: str = Field(..., alias="sessionId")

    model_config = ConfigDict(populate_by_name=True)


class PortalResponse(BaseModelConfig):
    """Billing portal."""
    url: str


class InvoiceResponse(BaseModelConfig):
    """Invoice (camelCase)."""
    id: str = Field(..., alias="id")
    stripe_invoice_id: str | None = Field(default=None, alias="stripeInvoiceId")
    amount_cents: int | None = Field(default=None, alias="amountCents")
    currency: str | None = Field(default=None, alias="currency")
    status: str | None = Field(default=None, alias="status")
    period_start: datetime | None = Field(default=None, alias="periodStart")
    period_end: datetime | None = Field(default=None, alias="periodEnd")
    paid_at: datetime | None = Field(default=None, alias="paidAt")
    invoice_pdf_url: str | None = Field(default=None, alias="invoicePdfUrl")
    created_at_utc: datetime | None = Field(default=None, alias="createdAtUtc")

    model_config = ConfigDict(populate_by_name=True)


# =============================================================================
# Tenant Models (Check server for actual format)
# =============================================================================


class CreateTenantRequest(BaseModelConfig):
    """Request to create tenant."""
    name: str


class UpdateTenantRequest(BaseModelConfig):
    """Request to update tenant."""
    name: str | None = None


class CurrentTenantResponse(BaseModelConfig):
    """Current tenant details (API key compatible) - uses snake_case with JsonPropertyName."""
    id: str
    name: str
    status: int | str  # Server returns enum value (int or string representation)
    status_text: str
    created_at_utc: datetime | None = None


class TenantResponse(BaseModelConfig):
    """Tenant details (Bearer auth) - uses snake_case with JsonPropertyName."""
    id: str
    name: str
    status: int
    status_text: str | None = None
    created_at_utc: datetime | None = None
    member_count: int | None = None
    current_user_role: int | None = None


class TenantMemberResponse(BaseModelConfig):
    """Tenant member."""
    user_id: str
    email: str
    display_name: str | None = None
    role: int
    role_text: str
    joined_at_utc: datetime | None = None


class AddTenantMemberRequest(BaseModelConfig):
    """Request to add member."""
    email: str
    role: int = 2


class UpdateMemberRoleRequest(BaseModelConfig):
    """Request to update role."""
    role: int


class TenantInvitationResponse(BaseModelConfig):
    """Tenant invitation."""
    id: str
    email: str
    role: int
    role_text: str
    status: int
    status_text: str
    invited_by: str
    invited_at_utc: datetime | None = None
    expires_at_utc: datetime | None = None

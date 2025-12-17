"""SendBase Email SDK - Official Python client for the SendBase Email API."""

from .client import SendBaseClient, AsyncSendBaseClient
from .exceptions import (
    SendBaseError,
    SendBaseAuthenticationError,
    SendBaseValidationError,
    SendBaseNotFoundError,
    SendBaseRateLimitError,
)
from .models import (
    # Email models
    SendEmailRequest,
    SendEmailResponse,
    EmailRecipient,
    EmailAttachment,
    BatchEmailItemResult,
    BatchEmailResponse,
    MessageResponse,
    # Domain models
    CreateDomainRequest,
    DomainResponse,
    DnsRecordResponse,
    # Template models
    CreateTemplateRequest,
    UpdateTemplateRequest,
    TemplateResponse,
    TemplatePreviewResponse,
    # Webhook models
    CreateWebhookRequest,
    UpdateWebhookRequest,
    WebhookResponse,
    WebhookCreatedResponse,
    WebhookEventTypeResponse,
    # Inbound models
    InboundAttachmentResponse,
    InboundMessageResponse,
    InboundDownloadResponse,
    # Billing models
    PlanResponse,
    SubscriptionResponse,
    UsageResponse,
    UsageSummaryResponse,
    LimitsResponse,
    # Tenant models
    CurrentTenantResponse,
)

__version__ = "1.0.0"
__all__ = [
    # Client
    "SendBaseClient",
    "AsyncSendBaseClient",
    # Exceptions
    "SendBaseError",
    "SendBaseAuthenticationError",
    "SendBaseValidationError",
    "SendBaseNotFoundError",
    "SendBaseRateLimitError",
    # Email models
    "SendEmailRequest",
    "SendEmailResponse",
    "EmailRecipient",
    "EmailAttachment",
    "BatchEmailItemResult",
    "BatchEmailResponse",
    "MessageResponse",
    # Domain models
    "CreateDomainRequest",
    "DomainResponse",
    "DnsRecordResponse",
    # Template models
    "CreateTemplateRequest",
    "UpdateTemplateRequest",
    "TemplateResponse",
    "TemplatePreviewResponse",
    # Webhook models
    "CreateWebhookRequest",
    "UpdateWebhookRequest",
    "WebhookResponse",
    "WebhookCreatedResponse",
    "WebhookEventTypeResponse",
    # Inbound models
    "InboundAttachmentResponse",
    "InboundMessageResponse",
    "InboundDownloadResponse",
    # Billing models
    "PlanResponse",
    "SubscriptionResponse",
    "UsageResponse",
    "UsageSummaryResponse",
    "LimitsResponse",
    # Tenant models
    "CurrentTenantResponse",
]

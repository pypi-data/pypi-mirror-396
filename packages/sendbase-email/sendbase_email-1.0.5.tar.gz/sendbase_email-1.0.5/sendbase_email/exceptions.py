"""SendBase SDK exceptions."""
from __future__ import annotations

from typing import Any


class SendBaseError(Exception):
    """Base exception for all SendBase SDK errors."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        error_code: str | None = None,
        request_id: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.request_id = request_id
        self.details = details or {}

    def __str__(self) -> str:
        parts = [self.message]
        if self.status_code:
            parts.append(f"(HTTP {self.status_code})")
        if self.error_code:
            parts.append(f"[{self.error_code}]")
        if self.request_id:
            parts.append(f"Request ID: {self.request_id}")
        return " ".join(parts)


class SendBaseAuthenticationError(SendBaseError):
    """Raised when authentication fails (401 Unauthorized)."""

    def __init__(
        self,
        message: str = "Authentication failed. Check your API key.",
        **kwargs: Any,
    ):
        super().__init__(message, status_code=401, **kwargs)


class SendBaseValidationError(SendBaseError):
    """Raised when request validation fails (400 Bad Request)."""

    def __init__(
        self,
        message: str = "Validation failed.",
        errors: dict[str, list[str]] | None = None,
        **kwargs: Any,
    ):
        super().__init__(message, status_code=400, **kwargs)
        self.errors = errors or {}

    def __str__(self) -> str:
        base = super().__str__()
        if self.errors:
            error_details = "; ".join(
                f"{field}: {', '.join(msgs)}" for field, msgs in self.errors.items()
            )
            return f"{base} - {error_details}"
        return base


class SendBaseNotFoundError(SendBaseError):
    """Raised when a resource is not found (404 Not Found)."""

    def __init__(
        self,
        message: str = "Resource not found.",
        resource_type: str | None = None,
        resource_id: str | None = None,
        **kwargs: Any,
    ):
        super().__init__(message, status_code=404, **kwargs)
        self.resource_type = resource_type
        self.resource_id = resource_id


class SendBaseRateLimitError(SendBaseError):
    """Raised when rate limit is exceeded (429 Too Many Requests)."""

    def __init__(
        self,
        message: str = "Rate limit exceeded.",
        retry_after: int | None = None,
        **kwargs: Any,
    ):
        super().__init__(message, status_code=429, **kwargs)
        self.retry_after = retry_after

    def __str__(self) -> str:
        base = super().__str__()
        if self.retry_after:
            return f"{base} Retry after {self.retry_after} seconds."
        return base

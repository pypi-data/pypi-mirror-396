"""Custom exceptions for the Finanfut Billing SDK."""

from __future__ import annotations

from typing import Any


class FinanfutBillingError(Exception):
    """Base exception for all SDK errors."""

    def __init__(self, message: str, *, status_code: int | None = None, payload: Any | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


class FinanfutBillingAuthError(FinanfutBillingError):
    """Raised when authentication fails."""


class FinanfutBillingValidationError(FinanfutBillingError):
    """Raised when the API returns validation errors."""


class FinanfutBillingServiceError(FinanfutBillingError):
    """Raised for domain errors returned by the service."""

    def __init__(
        self,
        message: str,
        *,
        error: str | None = None,
        request_id: str | None = None,
        status_code: int | None = None,
        payload: Any | None = None,
    ) -> None:
        super().__init__(message, status_code=status_code, payload=payload)
        self.error = error
        self.request_id = request_id


class FinanfutBillingHTTPError(FinanfutBillingError):
    """Raised for unexpected HTTP errors."""

"""Synchronous client for the Finanfut Billing External API."""

from __future__ import annotations

from typing import Any, Callable, Type, TypeVar, cast
from uuid import UUID

import requests
from pydantic import BaseModel

from .providers import ProvidersClient
from .errors import (
    FinanfutBillingAuthError,
    FinanfutBillingHTTPError,
    FinanfutBillingServiceError,
    FinanfutBillingValidationError,
)
from .models import (
    ExternalClientUpsertRequest,
    ExternalClientUpsertResponse,
    ExternalInvoiceCreateRequest,
    ExternalInvoiceCreateResponse,
    ExternalInvoiceDetailResponse,
    ExternalInvoiceEmailRequest,
    ExternalInvoiceEmailResponse,
    ExternalPaymentCreateRequest,
    ExternalPaymentCreateResponse,
    ExternalProviderUpsertRequest,
    ExternalProviderUpsertResponse,
    ExternalServiceUpsertRequest,
    ExternalServiceUpsertResponse,
    ExternalTaxRateListResponse,
    PartnerPaymentMethod,
    PartnerPaymentMethodCreate,
    Settlement,
    SettlementCreate,
    SettlementPayoutCreate,
)

_ResponseModel = TypeVar("_ResponseModel", bound=BaseModel)


class FinanfutBillingClient:
    """Synchronous client for Finanfut Billing External API (v1)."""

    def __init__(self, base_url: str, api_key: str, timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.settlements = SettlementsClient(self)
        self.partner_payment_methods = PartnerPaymentMethodsClient(self)
        self.providers = ProvidersClient(self)

    # Public API methods -------------------------------------------------
    def upsert_client(self, payload: ExternalClientUpsertRequest) -> ExternalClientUpsertResponse:
        """Create or update a client by external reference."""

        return self._post(
            "/external/v1/clients/upsert",
            payload.model_dump(exclude_none=True, by_alias=True),
            ExternalClientUpsertResponse,
        )

    def upsert_service(self, payload: ExternalServiceUpsertRequest) -> ExternalServiceUpsertResponse:
        """Create or update a service/product."""

        return self._post(
            "/external/v1/services/upsert",
            payload.model_dump(exclude_none=True, by_alias=True),
            ExternalServiceUpsertResponse,
        )

    def list_tax_rates(self) -> ExternalTaxRateListResponse:
        """Return active tax rates."""

        return self._get("/external/v1/tax-rates", ExternalTaxRateListResponse)

    def create_invoice(self, payload: ExternalInvoiceCreateRequest) -> ExternalInvoiceCreateResponse:
        """Create an invoice and return its identifiers."""

        return self._post(
            "/external/v1/invoices/create",
            payload.model_dump(exclude_none=True, by_alias=True),
            ExternalInvoiceCreateResponse,
        )

    def get_invoice(self, invoice_id: UUID | str) -> ExternalInvoiceDetailResponse:
        """Retrieve invoice details by ID."""

        return self._get(
            f"/external/v1/invoices/{invoice_id}",
            ExternalInvoiceDetailResponse,
        )

    def send_invoice_email(
        self,
        invoice_id: UUID | str,
        payload: ExternalInvoiceEmailRequest,
    ) -> ExternalInvoiceEmailResponse:
        """Send an invoice PDF via email."""

        return self._post(
            f"/external/v1/invoices/{invoice_id}/send-email",
            payload.model_dump(exclude_none=True, by_alias=True),
            ExternalInvoiceEmailResponse,
        )

    def register_payment(
        self,
        invoice_id: UUID | str,
        payload: ExternalPaymentCreateRequest,
    ) -> ExternalPaymentCreateResponse:
        """Register a payment for an invoice."""

        return self._post(
            f"/external/v1/invoices/{invoice_id}/payments",
            payload.model_dump(exclude_none=True, by_alias=True),
            ExternalPaymentCreateResponse,
        )

    # Internal helpers ---------------------------------------------------
    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _get(
        self,
        path: str,
        model: Type[_ResponseModel],
        *,
        params: dict[str, Any] | None = None,
        many: bool = False,
    ) -> _ResponseModel | list[_ResponseModel]:
        return self._request(requests.get, path, model, params=params, many=many)

    def _post(
        self,
        path: str,
        data: dict[str, Any],
        model: Type[_ResponseModel],
        *,
        many: bool = False,
    ) -> _ResponseModel | list[_ResponseModel]:
        return self._request(requests.post, path, model, json=data, many=many)

    def _request(
        self,
        method: Callable[..., requests.Response],
        path: str,
        model: Type[_ResponseModel],
        *,
        params: dict[str, Any] | None = None,
        many: bool = False,
        **kwargs: Any,
    ) -> _ResponseModel | list[_ResponseModel]:
        url = f"{self.base_url}{path}"
        response = method(url, headers=self._headers(), timeout=self.timeout, params=params, **kwargs)
        return self._handle_response(response, model, many=many)

    def _handle_response(
        self,
        response: requests.Response,
        model: Type[_ResponseModel],
        *,
        many: bool = False,
    ) -> _ResponseModel | list[_ResponseModel]:
        content_type = response.headers.get("content-type", "")
        is_json = "application/json" in content_type
        payload: Any | None = response.json() if is_json else None

        if 200 <= response.status_code < 300:
            if payload is None:
                raise FinanfutBillingHTTPError("Expected JSON response", status_code=response.status_code)
            if many:
                if not isinstance(payload, list):
                    raise FinanfutBillingHTTPError(
                        "Expected list response", status_code=response.status_code, payload=payload
                    )
                return [model.model_validate(item) for item in payload]
            return model.model_validate(payload)

        if response.status_code in {401, 403}:
            raise FinanfutBillingAuthError("Authentication failed", status_code=response.status_code, payload=payload)

        if response.status_code == 422:
            raise FinanfutBillingValidationError(
                "Request validation failed",
                status_code=response.status_code,
                payload=payload,
            )

        if isinstance(payload, dict) and payload.get("error"):
            raise FinanfutBillingServiceError(
                payload.get("message", "Service error"),
                error=payload.get("error"),
                request_id=payload.get("request_id"),
                status_code=response.status_code,
                payload=payload,
            )

        raise FinanfutBillingHTTPError(
            f"Unexpected HTTP {response.status_code}",
            status_code=response.status_code,
            payload=payload,
        )


class SettlementsClient:
    """Client helper for settlement workflows."""

    def __init__(self, transport: FinanfutBillingClient) -> None:
        self._transport = transport

    def create_settlement(self, payload: SettlementCreate) -> Settlement:
        return cast(
            Settlement,
            self._transport._post(
                "/external/v1/settlements",
                payload.model_dump(exclude_none=True, by_alias=True),
                Settlement,
            ),
        )

    def get_settlement(self, settlement_id: UUID | str) -> Settlement:
        return cast(
            Settlement,
            self._transport._get(f"/external/v1/settlements/{settlement_id}", Settlement),
        )

    def list_settlements(self, status: str | None = None) -> list[Settlement]:
        response = self._transport._get(
            "/external/v1/settlements", Settlement, params={"status": status} if status else None, many=True
        )
        return cast(list[Settlement], response)

    def finalize_settlement(self, settlement_id: UUID | str) -> Settlement:
        return cast(
            Settlement,
            self._transport._post(f"/external/v1/settlements/{settlement_id}/finalize", {}, Settlement),
        )

    def register_payout(self, settlement_id: UUID | str, payload: SettlementPayoutCreate) -> Settlement:
        return cast(
            Settlement,
            self._transport._post(
                f"/external/v1/settlements/{settlement_id}/payout",
                payload.model_dump(exclude_none=True, by_alias=True),
                Settlement,
            ),
        )


class PartnerPaymentMethodsClient:
    """Client helper for partner payment methods."""

    def __init__(self, transport: FinanfutBillingClient) -> None:
        self._transport = transport

    def create_partner_payment_method(self, payload: PartnerPaymentMethodCreate) -> PartnerPaymentMethod:
        return cast(
            PartnerPaymentMethod,
            self._transport._post(
                "/external/v1/partner-payment-methods",
                payload.model_dump(exclude_none=True, by_alias=True),
                PartnerPaymentMethod,
            ),
        )

    def list_partner_payment_methods(
        self, client_id: UUID | str | None = None, provider_id: UUID | str | None = None
    ) -> list[PartnerPaymentMethod]:
        response = self._transport._get(
            "/external/v1/partner-payment-methods",
            PartnerPaymentMethod,
            params={
                "client_id": str(client_id) if client_id else None,
                "provider_id": str(provider_id) if provider_id else None,
            },
            many=True,
        )
        return cast(list[PartnerPaymentMethod], response)

    def get_partner_payment_method(self, method_id: UUID | str) -> PartnerPaymentMethod:
        return cast(
            PartnerPaymentMethod,
            self._transport._get(
                f"/external/v1/partner-payment-methods/{method_id}",
                PartnerPaymentMethod,
            ),
        )

    def set_default_partner_payment_method(self, method_id: UUID | str) -> PartnerPaymentMethod:
        return cast(
            PartnerPaymentMethod,
            self._transport._post(
                f"/external/v1/partner-payment-methods/{method_id}/set-default",
                {},
                PartnerPaymentMethod,
            ),
        )

    def deactivate_partner_payment_method(self, method_id: UUID | str) -> PartnerPaymentMethod:
        return cast(
            PartnerPaymentMethod,
            self._transport._request(
                requests.delete,
                f"/external/v1/partner-payment-methods/{method_id}",
                PartnerPaymentMethod,
            ),
        )

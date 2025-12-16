from __future__ import annotations

from .models import ExternalProviderUpsertRequest, ExternalProviderUpsertResponse


class ProvidersClient:
    def __init__(self, transport):
        self._transport = transport

    def upsert_provider(
        self, payload: ExternalProviderUpsertRequest
    ) -> ExternalProviderUpsertResponse:
        return self._transport._post(
            "/external/v1/providers",
            payload.model_dump(exclude_none=True, by_alias=True),
            ExternalProviderUpsertResponse,
        )

    def get_provider(self, provider_id):
        return self._transport._get(
            f"/external/v1/providers/{provider_id}",
            ExternalProviderUpsertResponse,
        )

# Finanfut Billing Python SDK

Client oficial sincrònic per consumir la **Finanfut Billing External API (`/external/v1`)** amb models compatibles amb **Pydantic v2** i autenticació per API key.

## Instal·lació

Per instal·lar:

- Pydantic 2.x: `pip install finanfut-billing-sdk>=2.0`
- Pydantic 1.x: `pip install finanfut-billing-sdk<2.0`
- Des del repositori local: `pip install -e backend/sdk`

Dependències principals:

- `pydantic>=2.0,<3.0`
- `requests>=2.31`

## Configuració bàsica

```python
from finanfut_billing_sdk import FinanfutBillingClient

client = FinanfutBillingClient(
    base_url="https://billing.finanfut.com",
    api_key="sk_live_xxx",
)
```

## Documentació

La documentació completa del SDK s'ha dividit en seccions a `backend/sdk/docs/` i es publica via MkDocs. Consulta el contingut per temes:

- Introducció i instal·lació
- Configuració i autenticació
- Ús dels endpoints (clients, serveis, factures, pagaments, mètodes de pagament de partners, tipus d'IVA)
- Liquidacions (settlements)
- Gestió d'errors i bones pràctiques

Per generar la documentació localment:

```bash
cd backend/sdk
mkdocs serve --config-file mkdocs.yml
```

## Publicació a PyPI

El paquet està preparat per publicar-se a PyPI quan es creen tags `v*` al repositori. El workflow `publish-sdk.yml` valida la versió (`__version__`) i fa l'upload amb Twine.

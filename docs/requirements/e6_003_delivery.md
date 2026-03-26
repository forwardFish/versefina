# E6-003 Delivery

- Scope: reusable `MarketStyleEmbedding` generation from statement behavior features
- Routes:
  - `POST /api/v1/statements/{statement_id}/style-embedding`
  - `GET /api/v1/statements/{statement_id}/style-embedding`
- Guarantees:
  - produces deterministic structured embeddings from the same feature input
  - exposes holding-period distribution, momentum, mean-reversion, concentration, and latency signals
  - keeps low-confidence markers when upstream features are partial

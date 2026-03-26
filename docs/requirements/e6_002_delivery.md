# E6-002 Delivery

- Scope: statement behavior feature extraction for downstream style assets
- Routes:
  - `POST /api/v1/statements/{statement_id}/style-features`
  - `GET /api/v1/statements/{statement_id}/style-features`
- Guarantees:
  - extracts holding-period, add/reduce, momentum, and drawdown-tolerance features from parsed trade records
  - persists a reusable feature payload for later style embedding
  - marks partial / low-confidence outputs when trade samples are too thin

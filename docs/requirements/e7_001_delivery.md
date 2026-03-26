# E7-001 Delivery

- Scope: behavior mirror-agent assembly on top of style assets
- Routes:
  - `POST /api/v1/statements/{statement_id}/mirror-agent`
  - `GET /api/v1/statements/{statement_id}/mirror-agent`
- Guarantees:
  - mirror agents reference style embeddings, archetype seeds, and activation calibration
  - mirror-agent profile stays in the secondary-entry lane and does not replace the event mainline

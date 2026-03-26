# E7-003 Delivery

- Scope: distribution calibration tables and belief-pattern stats
- Routes:
  - `POST /api/v1/statements/{statement_id}/distribution-calibration`
  - `GET /api/v1/statements/{statement_id}/distribution-calibration`
- Guarantees:
  - tracks participant-segment calibration by event type
  - records belief-pattern hit/failure summaries for later reuse

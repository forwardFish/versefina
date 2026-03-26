# E7-002 Delivery

- Scope: mirror-agent validation grading
- Routes:
  - `POST /api/v1/statements/{statement_id}/mirror-agent/validation`
  - `GET /api/v1/statements/{statement_id}/mirror-agent/validation`
- Guarantees:
  - exposes `risk`, `noise`, `hold`, and `grading` outputs
  - supports provisional grading when evidence remains thin

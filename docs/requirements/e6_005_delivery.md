# E6-005 Delivery

- Scope: initial participant activation calibration rules from archetype seeds
- Routes:
  - `POST /api/v1/statements/{statement_id}/activation-calibration`
  - `GET /api/v1/statements/{statement_id}/activation-calibration`
- Guarantees:
  - produces minimal event-type to participant-family activation rules
  - keeps a default activation fallback when no dedicated rule matches
  - persists calibration assets for later prepare-orchestrator integration

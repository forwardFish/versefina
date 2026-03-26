# E2-005 Delivery

- Scope: participant default authority/risk registry, command routes, tests
- Route: `POST /api/v1/participants/registry`
- Route: `POST /api/v1/participants/registry/{participant_family}`
- Guarantees:
  - every participant family exposes a default `authority_weight`
  - every participant family exposes a default `risk_budget_profile`
  - registry snapshots are ready for later calibration-layer overrides

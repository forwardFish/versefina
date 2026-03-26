# E2-002 Delivery

- Scope: participant primary variants registry, container wiring, command routes, tests
- Route: `POST /api/v1/participants/variants`
- Route: `POST /api/v1/participants/variants/{participant_family}`
- Guarantees:
  - each participant family has one primary style variant
  - each variant defines `authority_weight` and `risk_budget_profile`
  - the registry can be reused by later participant preparation stories

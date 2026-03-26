# E1-005 Delivery

- Scope: casebook persistence, replay read path, query route, tests
- Route: `GET /api/v1/events/{event_id}`
- Route: `GET /api/v1/events/{event_id}/casebook`
- Guarantees:
  - raw record, structure, and mapping are linked by `event_id`
  - casebook replay returns explicit `not_found` when the sample is missing
  - prepared state is persisted for downstream validation

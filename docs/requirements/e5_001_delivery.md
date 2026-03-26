# E5-001 Delivery

- Scope: report card, review report, reusable reporting bundle, query routes, tests
- Routes:
  - `GET /api/v1/events/{event_id}/report-card`
  - `GET /api/v1/events/{event_id}/review-report`
- Guarantees:
  - report card combines event summary, graph summary, scenario pack, and simulation summary
  - review report exposes timeline, key reasons, and invalidation points
  - why-context fields are packaged for later retrieval APIs

# E3-001 Delivery

- Scope: belief graph schema, aggregation service, command route, container wiring, tests
- Route: `POST /api/v1/events/{event_id}/belief-graph`
- Guarantees:
  - participant roster output can be aggregated into a `BeliefGraphSnapshot`
  - the snapshot records at least `key_supporters` and `key_opponents`
  - the graph payload is ready for downstream scenario-engine consumption

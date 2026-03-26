# E5-005 Delivery

- Scope: why/retrieval report API backed by beliefs, simulation logs, and recorded outcomes
- Route:
  - `GET /api/v1/events/{event_id}/why`
- Guarantees:
  - returns structured evidence instead of generic prose
  - references belief-graph, simulation, outcome, and reliability context
  - degrades to `insufficient_evidence` when the process trail is incomplete

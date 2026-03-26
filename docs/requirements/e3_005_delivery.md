# E3-005 Delivery

- Scope: event-card projection service, query route, container wiring, tests
- Route: `GET /api/v1/events/{event_id}/card`
- Guarantees:
  - the event card aggregates event summary, participant summary, graph summary, three scenarios, watchpoints, and invalidation conditions
  - the card structure is stable enough for later reporting and query reuse
  - unfinished scenarios never masquerade as a ready card

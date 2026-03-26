# E1-003 Delivery

- Scope: event ingestion, structuring, command route, container wiring, tests
- Route: `POST /api/v1/events`
- Route: `POST /api/v1/events/{event_id}/prepare`
- Guarantees:
  - text-only event input is accepted for whitelist events
  - structure is normalized into `EventStructure`
  - mapping output is attached for downstream preparation and replay

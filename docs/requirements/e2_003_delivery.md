# E2-003 Delivery

- Scope: participant prepare orchestrator, roster schema, command route, container wiring, tests
- Route: `POST /api/v1/events/{event_id}/prepare`
- Guarantees:
  - prepare returns a `ParticipantRoster` for structured supply-chain price-shock events
  - each activated participant carries weights, style metadata, and activation reasons
  - thin-evidence events degrade explicitly instead of silently pretending to be ready

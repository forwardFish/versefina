# E4-002 Delivery

- Scope: lightweight simulation runner, event simulation workflow graph, command route, tests
- Route: `POST /api/v1/events/{event_id}/simulation/run`
- Guarantees:
  - a prepared simulation run can execute 3 to 5 rounds deterministically
  - each round updates participant state and emits reason codes
  - the final run payload is persisted back into the simulation runtime store

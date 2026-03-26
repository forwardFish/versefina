# E4-001 Delivery

- Scope: simulation prepare service, simulation schema, command route, container wiring, tests
- Route: `POST /api/v1/events/{event_id}/simulation/prepare`
- Guarantees:
  - a persisted `SimulationRun` seed is created before execution starts
  - each participant receives an initial state and planned role derived from the dominant scenario
  - the returned `runner_payload` is directly consumable by the later simulation runner

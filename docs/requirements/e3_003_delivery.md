# E3-003 Delivery

- Scope: three-case scenario schemas, scenario engine service, command route, container wiring, tests
- Route: `POST /api/v1/events/{event_id}/scenarios`
- Guarantees:
  - `base`, `bull`, and `bear` scenarios all include first movers, followers, watchpoints, and invalidation conditions
  - `dominant_scenario` is derived from explicit graph metrics
  - the scenario engine consumes belief-graph output instead of generating free-form placeholders

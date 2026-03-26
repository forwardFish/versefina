# E4-004 Delivery

- Scope: timeline extraction from simulation action logs, reusable summary payload, tests
- Guarantees:
  - timeline output groups `first_move`, `follow_on`, and `exit_chain`
  - timeline is derived from persisted action logs and round updates
  - turning points are surfaced so event cards and reports can reuse the same sequence

# E5-002 Delivery

- Scope: outcome backfill command flow, outcome persistence, review-report association, API tests
- Route:
  - `POST /api/v1/events/{event_id}/outcomes`
- Guarantees:
  - supports `t1` and `t3` outcome backfill
  - persists sector, leader, expansion, and sentiment outcome evidence
  - computes and stores `dominant_scenario_actual` plus `score_label`
  - review report can load the latest recorded outcome

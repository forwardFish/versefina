# E5-004 Delivery

- Scope: participant-family reliability aggregation for outcome review
- Route:
  - `GET /api/v1/events/{event_id}/reliability`
- Guarantees:
  - aggregates reliability by `participant_family`
  - exposes direction, early-detection, and invalidation-detection ability tags
  - marks low-sample-size results until enough events exist

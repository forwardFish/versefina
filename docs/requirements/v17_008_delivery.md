# V17-008 Delivery Notes

- Story: `V17-008`
- Goal: persist per-round action logs and participant state snapshots for the event sandbox runtime.

## Delivered Contracts

- Action logs are written to `.runtime/event_simulations/actions/<run_id>.jsonl`
- State snapshots are written to `.runtime/event_simulations/snapshots/<run_id>-<round_id>.json`
- Query routes expose:
  - `GET /api/v1/events/{event_id}/simulation/action-log`
  - `GET /api/v1/events/{event_id}/simulation/state-snapshots`

## Persisted Fields

- Action log entries include `actor_id`, `action_name`, `action_type`, `target_id`, `confidence`, `reason_code`, and state transition metadata.
- State snapshots preserve the participant states for each persisted round.

## Recovery Behavior

- Querying before a run exists returns `simulation_missing`.
- Completed runs remain queryable from file-backed runtime artifacts.

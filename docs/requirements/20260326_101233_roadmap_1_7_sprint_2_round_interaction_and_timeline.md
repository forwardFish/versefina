# roadmap_1_7_sprint_2_round_interaction_and_timeline

## Context
- Project: versefina
- Delivery mode: auto
- CEO review mode: hold_scope
- Source requirement file: inline input

## User Problem
# Sprint 2 Plan

## Target Audience
The primary product operators and analysts who depend on this sprint outcome.

## Requirement Summary
# Sprint 2 Plan

## Sprint Name
Round Interaction and Timeline

## Goal
Move from static participant preparation into a real multi-round interaction runtime with round boundaries, action logs, state snapshots, and timeline summaries.

## In Scope
- simulation prepare contract
- multi-round interaction engine
- action log and state snapshots
- first move / follow / exit timeline
- simulate command and round query surface

## Out Of Scope
- belief and market-state dynamics
- replay pages

## Recommended Execution Order
1. V17-006
2. V17-007
3. V17-008
4. V17-009
5. V17-010

Sprint roadmap_1_7_sprint_2_round_interaction_and_timeline should deliver the following story goals in one coordinated cycle:
- Create a simulation prepare step that turns an event seed and participant roster into a round-ready run boundary.
- Run multi-round participant decisions so not every participant acts every round and actions can change other actions.
- Persist per-round action logs and participant state snapshots so replay and belief updates can consume stable history.
- Project round history into first-move, follow-on, and exit timeline summaries that the sandbox page can narrate.
- Expose simulate command and round-level query APIs that make the interaction runtime observable from Swagger and the future UI.

## Product Constraints
- Follow the formal story execution matrix.
- Do not skip review, QA, or sprint close evidence.

## Success Signals
- Every story in the sprint completes with formal evidence.
- Sprint-level framing, closeout, and acceptance artifacts are recorded.

## CEO Mode Decision
- Selected mode: hold_scope
- No scope expansion was auto-accepted.

## System Audit Snapshot
- Design scope detected; keep plan-design-review in the downstream chain.
- Office-hours framing is available and should be treated as upstream context.
- Constraint count: 2 | Success signals: 2.

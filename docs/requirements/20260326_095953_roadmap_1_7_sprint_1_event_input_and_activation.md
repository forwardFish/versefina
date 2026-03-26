# roadmap_1_7_sprint_1_event_input_and_activation

## Context
- Project: versefina
- Delivery mode: auto
- CEO review mode: hold_scope
- Source requirement file: inline input

## User Problem
# Sprint 1 Plan

## Target Audience
The primary product operators and analysts who depend on this sprint outcome.

## Requirement Summary
# Sprint 1 Plan

## Sprint Name
Event Input and Activation

## Goal
Turn one incoming message into a durable event seed, structure it into a stable schema, activate the participant roster, and expose the first read model that the sandbox pages can consume.

## In Scope
- message input contract and rejection path
- event record and event structure persistence
- participant roster activation
- action protocol contract and initial participant state
- seed query surface for event and participants

## Out Of Scope
- multi-round simulation
- influence propagation
- replay pages

## Recommended Execution Order
1. V17-001
2. V17-002
3. V17-003
4. V17-004
5. V17-005

Sprint roadmap_1_7_sprint_1_event_input_and_activation should deliver the following story goals in one coordinated cycle:
- Define the message-to-event ingestion contract and persist an event seed with a structured rejection path.
- Structure an event seed into stable 1.7 fields including event type, targets, signals, invalidation, and confidence.
- Activate a participant roster from a structured event using 1.7 roster rules and initial authority weights.
- Define the P0 action protocol and initialize participant state so later rounds can emit structured actions.
- Expose the event seed and participant roster through query routes that the sandbox UI can consume directly.

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

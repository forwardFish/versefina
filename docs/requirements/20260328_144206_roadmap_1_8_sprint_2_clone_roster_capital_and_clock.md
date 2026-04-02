# roadmap_1_8_sprint_2_clone_roster_capital_and_clock

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
Clone Roster, Capital, and Clock

## Goal
Turn the population blueprint into clone-level roster objects with capital ranges, risk budgets, initial state, and execution window preferences.

## In Scope
- clone roster schema and persistence
- capital bucket and exposure ranges
- clone initial state and risk budget
- execution clock
- clone query APIs

## Out Of Scope
- influence-driven trade adjustments
- event-sandbox wall redesign

## Recommended Execution Order
1. V18-006
2. V18-007
3. V18-008
4. V18-009
5. V18-010

Sprint roadmap_1_8_sprint_2_clone_roster_capital_and_clock should deliver the following story goals in one coordinated cycle:
- Persist clone-level roster objects under one event instead of family-only participants.
- Assign capital bucket ranges, cash ranges, and exposure ranges to each clone.
- Initialize clone state, current cash summary, current position summary, confidence, attention, and risk budget profile.
- Attach preferred and avoided execution windows to each clone and expose the event execution clock.
- Expose event clone roster and clone detail read models for product and validation surfaces.

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
- No major UI scope detected from this requirement.
- Office-hours framing is available and should be treated as upstream context.
- Constraint count: 2 | Success signals: 2.

# roadmap_1_8_sprint_3_execution_action_v2_and_trade_ledger

## Context
- Project: versefina
- Delivery mode: auto
- CEO review mode: hold_scope
- Source requirement file: inline input

## User Problem
# Sprint 3 Plan

## Target Audience
The primary product operators and analysts who depend on this sprint outcome.

## Requirement Summary
# Sprint 3 Plan

## Sprint Name
Execution Action V2 and Trade Ledger

## Goal
Upgrade simulation from opinion-like actions to trade-like execution actions with position, cash, and window-aware ledger traces.

## In Scope
- ExecutionActionV2 schema
- order size and position/cash transitions
- clone behavior policy engine
- trade ledger
- simulation v2 trace API

## Out Of Scope
- influence-to-trade probability changes
- event-sandbox wall redesign

## Recommended Execution Order
1. V18-011
2. V18-012
3. V18-013
4. V18-014
5. V18-015

Sprint roadmap_1_8_sprint_3_execution_action_v2_and_trade_ledger should deliver the following story goals in one coordinated cycle:
- Define the new trade-like action schema for WATCH, VALIDATE, INIT_BUY, ADD_BUY, REDUCE, EXIT, BROADCAST_BULL, and BROADCAST_BEAR.
- Implement deterministic order-size ranges and position/cash transitions for init buy, add buy, reduce, and exit.
- Drive clone action choices from latency, threshold, confirmation, invalidation, follow, suppression, and exit rules.
- Persist trade ledger entries and round snapshots that are aware of execution windows and clone-level state changes.
- Expose simulation v2 traces through stable APIs for action, position, cash, and execution-window playback.

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

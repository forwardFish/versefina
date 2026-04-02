# roadmap_1_8_sprint_4_influence_to_trade_and_market_state_v2

## Context
- Project: versefina
- Delivery mode: auto
- CEO review mode: hold_scope
- Source requirement file: inline input

## User Problem
# Sprint 4 Plan

## Target Audience
The primary product operators and analysts who depend on this sprint outcome.

## Requirement Summary
# Sprint 4 Plan

## Sprint Name
Influence-to-Trade and Market State V2

## Goal
Make influence edges change trade behavior for clones and drive market-state, belief, and scenario evolution from simulation signals.

## In Scope
- InfluenceEdgeV2
- influence-to-trade resolver
- market state engine v2
- belief and scenario revision v2
- edge and state explanation API

## Out Of Scope
- graph-wall UI redesign
- scoreboards and validation boards

## Recommended Execution Order
1. V18-016
2. V18-017
3. V18-018
4. V18-019
5. V18-020

Sprint roadmap_1_8_sprint_4_influence_to_trade_and_market_state_v2 should deliver the following story goals in one coordinated cycle:
- Upgrade influence edges so each edge stores effect type, effect strength, lag, activation, expiration, and evidence trace.
- Use influence edges to modify clone entry, add, follow, reduce, exit, confidence, crowding, and fragility probabilities.
- Drive Dormant, Ignition, Propagating, Crowded, Fragile, and Invalidated through simulation signals rather than descriptive labels only.
- Revise belief and bull/base/bear scenarios directly from clone trading behavior and market-state changes.
- Expose explanation payloads for one influence edge and one market-state transition so the UI can support click-to-why behavior.

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

# roadmap_1_7_sprint_4_replay_report_and_validation

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
Replay, Report, and Validation

## Goal
Form a replayable, explainable, and post-validated event loop with summary schemas, report APIs, outcome hooks, reliability scoring, and validation read models.

## In Scope
- replay and summary schema
- report / review / why APIs
- T+1 / T+3 outcome hooks
- reliability and scoring labels
- replay / report / validation query surface

## Out Of Scope
- product pages

## Recommended Execution Order
1. V17-016
2. V17-017
3. V17-018
4. V17-019
5. V17-020

Sprint roadmap_1_7_sprint_4_replay_report_and_validation should deliver the following story goals in one coordinated cycle:
- Define replay-oriented summary schemas that package round history, market state, belief changes, and scenario changes into stable payloads.
- Expose report, review, and why APIs that summarize how the simulation evolved and why the final conclusion was chosen.
- Introduce T+1 and T+3 outcome write hooks and a validation read model that can compare simulated and actual outcomes.
- Calculate participant reliability, dominant scenario labels, and scoring summaries from simulation plus outcome data.
- Expose GET /replay, GET /report, and GET /validation surfaces so product pages can consume replay and validation directly.

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

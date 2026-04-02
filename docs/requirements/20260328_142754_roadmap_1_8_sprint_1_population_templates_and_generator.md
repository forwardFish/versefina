# roadmap_1_8_sprint_1_population_templates_and_generator

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
Population Templates and Generator

## Goal
Introduce population templates, family/style presets, and a generator that can turn one real event into a population-level participant blueprint instead of a family-only roster.

## In Scope
- population template schema and registry
- family and style variant preset library
- template selector based on event, regime, and lineage
- population generator service
- template and generator read model

## Out Of Scope
- clone trading actions
- influence-driven trade changes
- UI graph wall redesign

## Recommended Execution Order
1. V18-001
2. V18-002
3. V18-003
4. V18-004
5. V18-005

Sprint roadmap_1_8_sprint_1_population_templates_and_generator should deliver the following story goals in one coordinated cycle:
- Define PopulationTemplate, ParticipantFamilyTemplate, and CloneTemplate schema plus a registry that can persist reusable market population presets.
- Encode the eight participant families and their style variants as reusable template library entries.
- Select the right population template for an event using event type, market regime, and finahunt lineage.
- Generate a population blueprint with clone counts and family share distribution from the selected template.
- Expose population template and generated blueprint data through stable query endpoints and docs.

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

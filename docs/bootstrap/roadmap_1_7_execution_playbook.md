# roadmap_1_7 Execution Playbook

## Goal
- Treat `roadmap_1_7` as the authoritative Versefina delivery lane.
- Build a dynamic event sandbox where one incoming message can:
  - become an event seed
  - activate participant agents
  - trigger multi-round interaction and influence propagation
  - update belief, market state, and scenarios over time
  - surface the full process on product pages and audit surfaces

## Source Of Truth
- Main requirement doc:
  - `D:\lyh\agent\agent-frame\versefina\docs\需求文档\需求分析_1.7.md`
- Reusable input backlog:
  - `D:\lyh\agent\agent-frame\versefina\tasks\roadmap_1_6_*`
- Product validation surfaces:
  - `http://127.0.0.1:3000/roadmap-1-6-demo`
  - `http://127.0.0.1:8001/docs`
  - `http://127.0.0.1:8010/versefina/runtime`

## Non-Negotiable Execution Rules
- `agentsystem` is the only delivery channel for Versefina Sprint and Story work.
- Use `run-roadmap`, `run-sprint`, or `auto-deliver`; do not treat manual file editing as the primary delivery path.
- Every Story must go through the standard agent chain:
  - `requirement_analysis`
  - `architecture_review`
  - `workspace_prep`
  - `backend_dev` or `frontend_dev`
  - `database_dev` when schema or persistence changes
  - `sync_merge`
  - `code_style_reviewer`
  - `tester`
  - `runtime_qa` or `browser_qa`
  - `security_scanner`
  - `reviewer`
  - `code_acceptance`
  - `acceptance_gate`
  - `doc_writer`
- Every UI Story must also run:
  - `setup_browser_cookies`
  - `browse`
  - `plan_design_review`
  - `design_consultation`
  - `browser_qa`
  - `qa_design_review`
- Every Story boundary must update:
  - `NOW.md`
  - `STATE.md`
  - `DECISIONS.md`
  - `docs/handoff/current_handoff.md`
  - `.meta/versefina/continuity/continuity_manifest.json`
- Pause only at a Story boundary or a shared blocker boundary.

## Active Roadmap Structure
1. `roadmap_1_7_sprint_1_event_input_and_activation`
   - `V17-001` message input contract and event record
   - `V17-002` event structuring field output
   - `V17-003` participant roster activation
   - `V17-004` action protocol contract and initial participant state
   - `V17-005` event seed read model
2. `roadmap_1_7_sprint_2_round_interaction_and_timeline`
   - `V17-006` simulation prepare contract
   - `V17-007` participant interaction engine
   - `V17-008` action log and state snapshots
   - `V17-009` first move / follow / exit timeline
   - `V17-010` simulate command and round query APIs
3. `roadmap_1_7_sprint_3_influence_belief_market_dynamics`
   - `V17-011` influence graph service
   - `V17-012` belief graph dynamic update
   - `V17-013` market state machine
   - `V17-014` scenario reviser
   - `V17-015` belief and scenario query surface
4. `roadmap_1_7_sprint_4_replay_report_and_validation`
   - `V17-016` replay schema
   - `V17-017` report / review / why APIs
   - `V17-018` T+1 / T+3 outcome hooks
   - `V17-019` reliability and scoring labels
   - `V17-020` replay / report / validation query APIs
5. `roadmap_1_7_sprint_5_event_sandbox_pages`
   - `V17-021` event input page
   - `V17-022` sandbox overview page
   - `V17-023` replay page
   - `V17-024` participant detail page
   - `V17-025` validation and review page
6. `roadmap_1_7_sprint_6_authoritative_closeout`
   - `V17-026` acceptance pack and story evidence governance
   - `V17-027` runtime / dashboard / report / demo refresh
   - `V17-028` continuity completed boundary write-back
   - `V17-029` Swagger and browser acceptance evidence
   - `V17-030` final handoff / document release / retro

## Standard Commands
- Roadmap:
  - `python cli.py run-roadmap --project versefina --env test --tasks-root "D:\lyh\agent\agent-frame\versefina\tasks" --roadmap-prefix roadmap_1_7 --resume`
- Sprint:
  - `python cli.py run-sprint --project versefina --env test --sprint-dir "D:\lyh\agent\agent-frame\versefina\tasks\roadmap_1_7_sprint_1_event_input_and_activation"`
- Story:
  - `python cli.py auto-deliver --project versefina --env test --prefix roadmap_1_7 --auto-run`

## Mid-Process Validation
- After each Story:
  - inspect `NOW.md`
  - inspect `docs/handoff/current_handoff.md`
  - inspect `.meta/versefina/continuity/continuity_manifest.json`
  - confirm the Story admission, failure, or handoff artifacts exist under `tasks/runtime`
- After each Sprint:
  - run `python -m pytest apps/api/tests -q`
  - open `http://127.0.0.1:8001/docs`
  - open `http://127.0.0.1:8010/versefina/runtime`
  - inspect the Sprint `special_acceptance_report.json`
- After Sprint 5:
  - confirm the product pages can show event input, multi-round interaction, influence propagation, belief and market state changes, and replay/validation outputs
- After Sprint 6:
  - confirm dashboard, report, continuity, and handoff all point to the same completed boundary

## Final Effect Checklist
- Product pages show:
  - one message becoming an event
  - participants activating and acting round by round
  - influence propagation and interaction paths
  - belief, market state, and scenario changes over time
  - replay, report, and validation surfaces
- Swagger exposes the event-sandbox API chain end to end.
- Runtime audit dashboard shows:
  - roadmap / sprint / story progress
  - evidence links
  - current or completed continuity boundary

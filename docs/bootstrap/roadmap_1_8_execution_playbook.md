# roadmap_1_8 Execution Playbook

## Goal
Execute `roadmap_1_8` through `agentsystem` as the only delivery channel for Versefina.

## Command
```powershell
cd D:\lyh\agent\agent-frame\agentsystem
python cli.py run-roadmap --project versefina --env test --tasks-root "D:\lyh\agent\agent-frame\versefina\tasks" --roadmap-prefix roadmap_1_8 --resume
```

## Execution Rules
- Only run through `agentsystem`.
- Do not skip Sprint or Story boundaries.
- UI stories must include `browse`, `plan_design_review`, `design_consultation`, `browser_qa`, and `qa_design_review`.
- Any blocker must stop at the current Story boundary with continuity and handoff updated.

## Story Boundary Writeback
- `NOW.md`
- `STATE.md`
- `DECISIONS.md`
- `docs/handoff/current_handoff.md`
- `.meta/versefina/continuity/continuity_manifest.json`

## Start Boundary
- Backlog: `roadmap_1_8`
- Sprint: `roadmap_1_8_sprint_1_population_templates_and_generator`
- Story: `V18-001`

## Source Of Truth
- `docs/需求文档/需求分析_1.8_最终融合版.md`
- `docs/reports/20260327_roadmap_1_7_与_1_6对照总结.md`

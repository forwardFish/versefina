# roadmap_1_6_sprint_4_lightweight_simulation_runtime

## Context
- Project: versefina
- Delivery mode: auto
- CEO review mode: hold_scope
- Source requirement file: inline input

## User Problem
# Sprint 4 规划

## Target Audience
The primary product operators and analysts who depend on this sprint outcome.

## Requirement Summary
# Sprint 4 规划

## Sprint 名称

轻量模拟运行层

## Sprint 目标

在 Belief Graph 和三剧本基线之上，补齐 `simulation_prepare`、`simulation_runner`、动作日志、状态快照和参与者时序链，形成一个可解释、可回放的事件轻量模拟闭环。

## 做什么

- [ ] 完成 `simulation_prepare`
- [ ] 完成 `simulation_runner`
- [ ] 完成 `actions.jsonl / state snapshots`
- [ ] 完成首动 / 跟随 / 撤退时序链
- [ ] 完成仿真结果反写 `BeliefGraph / ScenarioCard`

## 不做什么

- [ ] 不做 T+1 / T+3 结果回填
- [ ] 不做 why 查询
- [ ] 不做交割单风格资产

## Epic 总览

| Epic | Story 数 | 核心职责 |
| :--- | :--- | :--- |
| Epic 4.1 Simulation Runtime | 3 | prepare、runner 和日志体系 |
| Epic 4.2 Timeline & Feedback | 2 | 时序链和 graph / scenario 反写 |

## 推荐执行顺序

1. E4-001
2. E4-002
3. E4-003
4. E4-004
5. E4-005

Sprint roadmap_1_6_sprint_4_lightweight_simulation_runtime should deliver the following story goals in one coordinated cycle:
- 从 BeliefGraphSnapshot 和 ScenarioCard 生成参与者初始状态。
- 执行 3 到 5 轮轻量模拟，驱动参与者状态变化。
- 把轻量模拟过程写成 actions.jsonl 和 state snapshots。
- 从动作日志中提炼谁先动、谁跟随、谁撤退的时序链。
- 将轻量模拟结果反写到 BeliefGraphSnapshot 和 ScenarioCard。

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

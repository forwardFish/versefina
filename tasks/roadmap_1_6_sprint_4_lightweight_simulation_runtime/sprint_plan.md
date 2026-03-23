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

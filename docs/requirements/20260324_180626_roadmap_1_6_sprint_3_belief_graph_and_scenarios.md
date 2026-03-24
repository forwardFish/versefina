# roadmap_1_6_sprint_3_belief_graph_and_scenarios

## Context
- Project: versefina
- Delivery mode: auto
- CEO review mode: hold_scope
- Source requirement file: inline input

## User Problem
# Sprint 3 规划

## Target Audience
The primary product operators and analysts who depend on this sprint outcome.

## Requirement Summary
# Sprint 3 规划

## Sprint 名称

Belief Graph 与三剧本基线

## Sprint 目标

把参与者输出聚合成可计算的共识 / 分歧结构，完成 Belief Graph 指标、三剧本生成、观察点与失效条件服务，并形成面向产品展示的事件推演卡 `read model v1`。

## 做什么

- [ ] 完成 `BeliefGraphSnapshot` 构建器
- [ ] 完成核心 graph metrics
- [ ] 完成 `base / bull / bear` 三剧本引擎
- [ ] 完成 `watchpoints / invalidation` 服务
- [ ] 完成事件推演卡 read model

## 不做什么

- [ ] 不做轻量模拟
- [ ] 不做动作日志
- [ ] 不做 T+1 / T+3 回填

## Epic 总览

| Epic | Story 数 | 核心职责 |
| :--- | :--- | :--- |
| Epic 3.1 Graph Aggregation | 2 | 构建 Belief Graph 和核心聚合指标 |
| Epic 3.2 Scenario Baseline | 3 | 三剧本、观察点和事件卡 |

## 推荐执行顺序

1. E3-001
2. E3-002
3. E3-003
4. E3-004
5. E3-005

Sprint roadmap_1_6_sprint_3_belief_graph_and_scenarios should deliver the following story goals in one coordinated cycle:
- 把 ParticipantBelief 聚合成 BeliefGraphSnapshot。
- 完成 consensus、dissent、crowding、fragility 等 graph 核心指标。
- 基于 EventStructure 和 BeliefGraphSnapshot 生成 base / bull / bear 三剧本。
- 输出统一的 key_watchpoints 和 invalidation_conditions 服务。
- 把事件摘要、graph 指标和三剧本聚合成事件推演卡 read model。

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

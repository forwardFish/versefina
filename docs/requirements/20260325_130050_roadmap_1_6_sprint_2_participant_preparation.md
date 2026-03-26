# roadmap_1_6_sprint_2_participant_preparation

## Context
- Project: versefina
- Delivery mode: auto
- CEO review mode: hold_scope
- Source requirement file: inline input

## User Problem
# Sprint 2 规划

## Target Audience
The primary product operators and analysts who depend on this sprint outcome.

## Requirement Summary
# Sprint 2 规划

## Sprint 名称

金融参与者准备层

## Sprint 目标

在结构化事件的基础上，完成 8 类参与者统一输出协议、参与者家族和主变体定义、`prepare orchestrator`、证据与失效条件标准化、以及 `authority_weight / risk_budget` 注册表，让事件进入真正可运行的参与者预演状态。

## 做什么

- [ ] 建立 8 类参与者统一输出协议
- [ ] 定义参与者家族与主变体
- [ ] 完成 `prepare orchestrator`
- [ ] 标准化 evidence / trigger / invalidation
- [ ] 建立 authority weight / risk budget 注册表

## 不做什么

- [ ] 不做 Belief Graph 聚合
- [ ] 不生成最终三剧本
- [ ] 不做轻量模拟与日志

## Epic 总览

| Epic | Story 数 | 核心职责 |
| :--- | :--- | :--- |
| Epic 2.1 Participant Protocol | 3 | 定义协议、主变体和 roster 生成入口 |
| Epic 2.2 Evidence & Registry | 2 | 固定证据口径与权重注册表 |

## 推荐执行顺序

1. E2-001
2. E2-002
3. E2-003
4. E2-004
5. E2-005

Sprint roadmap_1_6_sprint_2_participant_preparation should deliver the following story goals in one coordinated cycle:
- 建立 8 类参与者统一输入输出协议。
- 给 8 类参与者补齐 participant_family 和 style_variant 主变体定义。
- 把结构化事件转成一次可运行的 Participant Roster，并统一 prepare 入口。
- 固定 evidence、trigger_conditions、invalidation_conditions 的标准结构。
- 建立参与者 authority weight 和 risk budget 的初始注册表。

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

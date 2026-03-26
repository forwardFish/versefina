# roadmap_1_6_sprint_5_review_and_outcome_validation

## Context
- Project: versefina
- Delivery mode: auto
- CEO review mode: hold_scope
- Source requirement file: inline input

## User Problem
# Sprint 5 规划

## Target Audience
The primary product operators and analysts who depend on this sprint outcome.

## Requirement Summary
# Sprint 5 规划

## Sprint 名称

复盘报告与后验验证

## Sprint 目标

在事件推演卡和轻量模拟结果之上，完成 `Report Card / Review Report`、T+1 / T+3 `Outcome Tracker`、`dominant_scenario` 判分、参与者可靠性统计和 why 追问接口，形成真正可验证的事件沙盘闭环。

## 做什么

- [ ] 完成 `Report Card / Review Report`
- [ ] 完成 T+1 / T+3 `Outcome Tracker`
- [ ] 完成 `dominant_scenario` 判分
- [ ] 完成 `participant segment reliability`
- [ ] 完成 `why / retrieval report`

## 不做什么

- [ ] 不做交割单解析增强
- [ ] 不做镜像 Agent 运行
- [ ] 不做分布级校准

## Epic 总览

| Epic | Story 数 | 核心职责 |
| :--- | :--- | :--- |
| Epic 5.1 Review & Outcomes | 3 | 报告、回填和剧本判分 |
| Epic 5.2 Reliability & Why | 2 | 参与者可靠性和追问接口 |

## 推荐执行顺序

1. E5-001
2. E5-002
3. E5-003
4. E5-004
5. E5-005

Sprint roadmap_1_6_sprint_5_review_and_outcome_validation should deliver the following story goals in one coordinated cycle:
- 生成对外可展示的 Report Card 和对内可复盘的 Review Report。
- 建立 T+1 / T+3 后验回填对象和回填流程。
- 定义 dominant_scenario 的判定规则和 hit / partial_hit / invalidated 等判分标签。
- 统计哪类参与者在当前事件类型中更可靠。
- 定义 why 查询接口，允许用户追问“为什么这样判断、为什么失效”。

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

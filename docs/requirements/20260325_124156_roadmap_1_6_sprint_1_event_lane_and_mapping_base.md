# roadmap_1_6_sprint_1_event_lane_and_mapping_base

## Context
- Project: versefina
- Delivery mode: auto
- CEO review mode: hold_scope
- Source requirement file: inline input

## User Problem
# Sprint 1 规划

## Target Audience
The primary product operators and analysts who depend on this sprint outcome.

## Requirement Summary
# Sprint 1 规划

## Sprint 名称

事件通道与题材映射基座

## Sprint 目标

冻结 Versefina 1.6 的首发事件范围，只支持“涨价链 / 供给冲击 / 产业链传导”，并建立 `EventRecord / EventStructure` 契约、事件结构化输入、题材映射字典和事件样本台账，为后续参与者准备层提供稳定输入。

## 做什么

- [ ] 冻结首发事件白名单
- [ ] 定义 `EventRecord / EventStructure` 契约与状态机
- [ ] 完成事件输入与结构化抽取服务规划
- [ ] 建立题材映射与标的池字典 `v0.1`
- [ ] 建立事件样本台账与回放基座

## 不做什么

- [ ] 不实现 8 类参与者输出
- [ ] 不实现 Belief Graph 聚合
- [ ] 不实现三剧本与轻量模拟

## Epic 总览

| Epic | Story 数 | 核心职责 |
| :--- | :--- | :--- |
| Epic 1.1 Event Lane & Contracts | 3 | 冻结首发事件、定义契约和输入服务 |
| Epic 1.2 Mapping & Casebook | 2 | 维护题材映射资产和事件样本回放基座 |

## 推荐执行顺序

1. E1-001
2. E1-002
3. E1-003
4. E1-004
5. E1-005

Sprint roadmap_1_6_sprint_1_event_lane_and_mapping_base should deliver the following story goals in one coordinated cycle:
- 冻结 1.6 第一阶段唯一支持的事件类型，只允许涨价链 / 供给冲击 / 产业链传导进入主流程。
- 定义 EventRecord / EventStructure 的 schema、状态机和最小字段集合。
- 规划并定义事件输入服务和结构化抽取服务的最小实现边界。
- 建立首发事件类型所需的商品 -> 产业链 -> 行业 -> 标的池 -> 风格标签映射资产。
- 建立事件样本台账和回放基座，沉淀可复跑的真实事件样本。

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

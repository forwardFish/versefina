# Sprint 5 规划

## Sprint 名称

事件反身性基线与样本台账

## Sprint 目标

把 `需求分析_1.2.md` 的事件推演方向收敛成 Versefina 可执行的第一条主线：先只支持“政策催化”事件，完成事件契约、原始事件接入、结构化抽取、监控信号/失效条件标准化和样本回放基座，为后续 8 Agent、Belief Graph 和三剧本提供稳定输入。

## 做什么

- [ ] 冻结首发事件范围与事件契约
- [ ] 落地 `Event Ingestion Service`
- [ ] 完成结构化事件抽取
- [ ] 标准化 `monitor_signals` 与 `invalidation_conditions`
- [ ] 建立 MVP 事件样本台账与回放基座

## 不做什么

- [ ] 不在本 Sprint 内完成 8 类 Agent 立场生成
- [ ] 不在本 Sprint 内实现 Belief Graph 聚合和三剧本推演
- [ ] 不在本 Sprint 内完成前端事件卡页面

## Epic 总览

| Epic | Story 数 | 核心职责 |
| :--- | :--- | :--- |
| Epic 5.1 Event Intake & Contracts | 2 | 收敛首发事件范围、定义契约并完成原始事件接入 |
| Epic 5.2 Structuring & Casebook | 3 | 完成结构化抽取、信号标准化和样本回放基座 |

## 推荐执行顺序

1. S5-001
2. S5-002
3. S5-003
4. S5-004
5. S5-005

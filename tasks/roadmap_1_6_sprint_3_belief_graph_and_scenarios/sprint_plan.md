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

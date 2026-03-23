# Versefina 1.6 Sprint 总览

## 规划目标

本规划服务于 `需求分析_1.6_最终版_事件参与者优先.md`，是 Versefina 后续开发的主路线 backlog。

核心原则：

- 第一主线改为：事件驱动的金融参与者预演
- 第一阶段先完成事件沙盘 MVP
- 交割单与镜像 Agent 保留，但下沉为第二阶段增强路线
- 不覆盖旧 `sprint_1` 到 `sprint_9` 资产

---

## Sprint 总览

| Sprint | 状态 | 优先级 | Story 数 | 核心目标 |
| :--- | :--- | :--- | :--- | :--- |
| Sprint 1 事件通道与题材映射基座 | 📋 新增 | P0 | 5 | 冻结首发事件、完成事件契约、结构化和题材映射基座 |
| Sprint 2 金融参与者准备层 | 📋 新增 | P0 | 5 | 跑通 8 类参与者统一协议、主变体和 prepare orchestrator |
| Sprint 3 Belief Graph 与三剧本基线 | 📋 新增 | P0 | 5 | 跑通共识 / 分歧聚合、三剧本和事件推演卡 |
| Sprint 4 轻量模拟运行层 | 📋 新增 | P0 | 5 | 跑通 simulation prepare、runner、动作日志和时序链 |
| Sprint 5 复盘报告与后验验证 | 📋 新增 | P0 | 5 | 跑通 report、T+1 / T+3 验证、判分和 why 查询 |
| Sprint 6 交割单到风格资产 | 📋 新增 | P1 | 5 | 将交割单链路转化为风格向量、原型母体和激活校准资产 |
| Sprint 7 镜像 Agent 与分布校准闭环 | 📋 新增 | P1 | 5 | 完成镜像 Agent、验证分级和分布级校准闭环 |

---

## 执行优先级策略

### P0 主链

1. Sprint 1
2. Sprint 2
3. Sprint 3
4. Sprint 4
5. Sprint 5

### P1 增强链

1. Sprint 6
2. Sprint 7

---

## 推荐执行顺序

### 阶段一：事件沙盘 MVP

1. Sprint 1：固定事件范围、结构化契约和题材映射底座
2. Sprint 2：把事件变成参与者 roster 和标准化 beliefs
3. Sprint 3：把 beliefs 变成 Belief Graph、三剧本和事件卡
4. Sprint 4：引入 3 到 5 轮轻量模拟与动作日志
5. Sprint 5：补齐复盘报告、T+1 / T+3 验证与 why 查询

### 阶段二：风格校准增强

1. Sprint 6：把交割单路线降为风格资产生产线
2. Sprint 7：完成镜像 Agent 与分布校准闭环

---

## 总计

- Sprint 数量：7
- Story 总数：35
- 第一阶段 MVP：Sprint 1-5
- 第二阶段增强：Sprint 6-7

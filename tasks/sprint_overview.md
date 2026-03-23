# Versefina Sprint 全景规划

## 规划目标

Versefina 项目包含三条需求线索：

1. `需求分析_1.1.md`：交割单驱动的行为镜像 Agent
2. `需求分析_1.2.md`：金融反身性引擎 / 事件推演系统
3. `需求分析_1.3_Aaru增强改造版.md`：市场参与者仿真层（Aaru 范式增强）

本规划将三条线索整合为 9 个 Sprint，覆盖从交割单上传到市场参与者仿真的完整产品闭环。

## Sprint 总览

| Sprint | 状态 | 优先级 | Story 数 | 核心目标 |
| :--- | :--- | :--- | :--- | :--- |
| Sprint 1 交割单到 Agent 建模 | ✅ 已完成 | P0 | 10 | 跑通上传、解析、基础画像与 Agent 创建闭环 |
| Sprint 2 世界、撮合、账本、日循环 | 🔄 进行中 | P0 | 7 | 跑通统一世界、撮合、账本与 Daily Loop |
| Sprint 3 行为镜像建模与策略壳 | 📋 已规划 | P1 | 6 | 把"画像"升级为"可运行、可约束"的行为镜像 Agent |
| Sprint 4 验证分级与只读运营控制 | 📋 已规划 | P1 | 7 | 把"可运行 Agent"升级为"可验证、可分级、可只读运营"的产品闭环 |
| Sprint 5 事件反身性基线与样本台账 | 📋 新增 | P0 | 5 | 冻结首发事件范围，建立事件契约、结构化输出和样本回放基座 |
| Sprint 6 Agent 社会与 Belief Graph | 📋 新增 | P0 | 5 | 跑通 8 类 Agent 的结构化立场输出与信念图谱聚合 |
| Sprint 7 三剧本推演与后验验证闭环 | 📋 新增 | P0 | 5 | 跑通资金状态迁移、三剧本、T+1/T+3 回填与 Agent 打分 |
| Sprint 8 事件产品化与 MVP 验收 | 📋 新增 | P1 | 4 | 完成事件卡、复盘页、批量验证与 MVP 验收包 |
| Sprint 9 市场参与者仿真层（Aaru 增强） | 📋 新增 | P2 | 5 | 补充 MarketStyleEmbedding、Archetype Seed、参与者家族增强和分布校准 |

## 执行优先级策略

### P0 优先级（必须完成）
1. **Sprint 1**：已完成，是所有后续 Sprint 的基础
2. **Sprint 2**：进行中，是 Agent 运行的底座
3. **Sprint 5-7**：事件反身性引擎核心闭环，是产品差异化的关键

### P1 优先级（重要但可延后）
1. **Sprint 3-4**：行为镜像增强和验证分级，提升 Agent 质量
2. **Sprint 8**：事件产品化，完成 MVP 验收

### P2 优先级（增强功能）
1. **Sprint 9**：Aaru 范式增强，提升系统的参与者仿真能力

## 建议执行顺序

### 第一阶段：基础闭环（Sprint 1-2）
1. 完成并整理 Sprint 2 本地改动
2. 确保 Sprint 1 + Sprint 2 的完整闭环可用

### 第二阶段：事件反身性引擎（Sprint 5-7）
1. 执行 Sprint 5，统一事件契约、事件样本和结构化字段
2. 执行 Sprint 6，把 8 类 Agent 和 Belief Graph 跑通
3. 执行 Sprint 7，完成三剧本推演和后验验证闭环

### 第三阶段：产品化与增强（Sprint 3-4, 8-9）
1. 执行 Sprint 3-4，提升行为镜像 Agent 质量
2. 执行 Sprint 8，完成事件产品化和 MVP 验收
3. 执行 Sprint 9，补充市场参与者仿真层

## Sprint 详细信息

### Sprint 1: 交割单到 Agent 建模（10 个 story）

**Epic 1.1: Statement Upload & Parse**
- S1-001: 交割单上传接口
- S1-002: Statement 状态机
- S1-003: 文件类型识别
- S1-004: 上传失败处理

**Epic 1.2: Parse & Standardize**
- S1-005: 字段映射规则
- S1-006: TradeRecord 标准化
- S1-007: 解析校验与错误报告

**Epic 1.3: Profile & Agent Creation**
- S1-008: Profile 提取
- S1-009: 风格标签与风控约束生成
- S1-010: Agent 创建 API

### Sprint 2: 世界、撮合、账本、日循环（7 个 story）

**Epic 2.1: World Foundation**
- S2-001: 统一市场世界初始化
- S2-002: 行情数据接入与日线价格服务

**Epic 2.2: Matching & Execution**
- S2-003: 撮合引擎与订单执行
- S2-004: 账本与持仓管理

**Epic 2.3: Daily Loop**
- S2-005: Agent 决策接口与信号生成
- S2-006: 日循环调度器
- S2-007: 绩效计算与快照

### Sprint 3: 行为镜像建模与策略壳（6 个 story）

**Epic 3.1: Feature & Profile**
- S3-001: 交易行为特征提取
- S3-002: 行为画像生成

**Epic 3.2: Template & Policy**
- S3-003: 模板库 v1
- S3-004: 模板匹配器
- S3-005: 行为镜像策略
- S3-006: 行为镜像 Agent 组装

### Sprint 4: 验证分级与只读运营控制（7 个 story）

- S4-001: 留出集验证管道
- S4-002: 评分引擎
- S4-003: Agent 分级
- S4-004: 验证报告只读视图
- S4-005: 结构化解释
- S4-006: 可见性与分享控制
- S4-007: 暂停、删除与数据移除

### Sprint 5: 事件反身性基线与样本台账（5 个 story）

- S5-001: 启动事件通道与契约
- S5-002: 事件摄入服务
- S5-003: 结构化字段与验证口径
- S5-004: 样本台账与回放基座
- S5-005: 首发事件类型冻结

### Sprint 6: Agent 社会与 Belief Graph（5 个 story）

- S6-001: 8 类 Agent 定义与角色契约
- S6-002: 8 类 Agent 结构化输出
- S6-003: Belief Graph 聚合
- S6-004: 共识结构演化
- S6-005: 拥挤度与脆弱性指标

### Sprint 7: 三剧本推演与后验验证闭环（5 个 story）

- S7-001: 资金状态迁移引擎
- S7-002: 三剧本生成器
- S7-003: T+1/T+3 回填与复盘
- S7-004: Outcome Tracker
- S7-005: Agent 打分与权重调整

### Sprint 8: 事件产品化与 MVP 验收（4 个 story）

- S8-001: 事件卡片与详情页
- S8-002: 复盘页与验证报告
- S8-003: 批量验证与历史回溯
- S8-004: MVP 验收包与里程碑

### Sprint 9: 市场参与者仿真层（Aaru 增强）（5 个 story）

**Epic 9.1: Style Embedding**
- S9-001: MarketStyleEmbedding 风格向量化
- S9-002: Archetype Seed 风格母体抽象

**Epic 9.2: Participant Family**
- S9-003: 8 类 Agent 增强为参与者家族
- S9-004: Belief Graph 增强参与者构成字段

**Epic 9.3: Distribution Calibration**
- S9-005: Distribution Calibration 分布校准

## 技术栈

- **前端**: Next.js 15 (TypeScript, React 19, Ant Design)
- **后端**: FastAPI (Python 3.11)
- **Worker**: Celery
- **数据库**: PostgreSQL
- **包管理**: pnpm (前端), pip (后端)
- **行情数据**: akshare（免费）
- **调度**: APScheduler 或 Celery Beat

## 总计

- **Sprint 数量**: 9 个
- **Story 总数**: 54 个
- **Epic 总数**: 20 个
- **预计工期**: 6-9 个月（按优先级分阶段执行）

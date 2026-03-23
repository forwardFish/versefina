# Sprint 9: 市场参与者仿真层（Aaru 增强）

## Sprint 目标

基于需求分析_1.3（Aaru 增强改造版），在不推翻现有 v1.1 和 v1.2 闭环的前提下，补充市场参与者仿真层，引入 MarketStyleEmbedding、Archetype Seed、参与者家族增强和分布校准能力。

## Epic 划分

### Epic 9.1: Style Embedding
- S9-001: MarketStyleEmbedding 风格向量化
- S9-002: Archetype Seed 风格母体抽象

### Epic 9.2: Participant Family
- S9-003: 8 类 Agent 增强为参与者家族
- S9-004: Belief Graph 增强参与者构成字段

### Epic 9.3: Distribution Calibration
- S9-005: Distribution Calibration 分布校准

## 关键里程碑

1. **风格向量化**（S9-001 ~ S9-002）：交易行为可向量化，风格母体可抽象
2. **参与者增强**（S9-003 ~ S9-004）：8 类 Agent 升级为参与者家族
3. **分布校准**（S9-005）：长期命中率积累，形成数据壁垒

## 验收标准

- 每个 Agent 都有 MarketStyleEmbedding
- Archetype Seed 可从 Agent 抽象生成
- 8 类 Agent 都有 participant_family 和 style_variant 字段
- Belief Graph 包含参与者构成信息
- Distribution Calibration 能够按事件类型记录命中率

## 依赖

- Sprint 1 全部完成（Profile 提取）
- Sprint 3 全部完成（行为特征提取）
- Sprint 6 全部完成（8 类 Agent 结构化输出、Belief Graph）
- Sprint 7 S7-004 完成（Outcome Tracker）

## 改造原则（来自需求分析_1.3）

- **不推翻现有系统**：v1.1 和 v1.2 的核心闭环保留不动
- **只补中间层**：在现有 Agent 和 Belief Graph 上增加参与者维度
- **MVP 优先**：先做 P1（MarketStyleEmbedding），再做 P2（8 Agent 增强），P3（Belief Graph 增强），P4（分布校准）

# Belief Graph 指标说明

## 1. 目标

Belief Graph 不是展示层包装，而是 Scenario Engine、轻量模拟和后验验证共同依赖的中间状态。

---

## 2. P0 核心指标

### `consensus_strength`

当前事件下支持同一主线的参与者强度。

### `dissent_width`

当前事件下反对或犹豫声音的宽度。

### `confidence_dispersion`

参与者置信度的离散程度，用于判断是否出现“表面一致、实际分裂”。

### `crowding_score`

当前主线是否已出现拥挤交易 / 拥挤共识。

### `falsification_fragility`

当前主线对少数关键条件是否过度依赖，是否容易被证伪。

### `key_supporters`

构成主流共识的关键参与者集合。

### `key_opponents`

构成反对或风险提醒的关键参与者集合。

---

## 3. P1 预留指标

以下字段第一阶段可先保留结构，不强制全量启用：

- `consensus_composition`
- `dissent_composition`
- `conviction_skew`
- `slow_fast_divergence`
- `style_rotation_probability`
- `reversal_risk`

---

## 4. 计算原则

- 指标必须真实消费参与者结构化输出
- 指标必须可重复计算
- 指标变化必须能解释
- 不允许只为了展示而虚设字段

---

## 5. 结果使用要求

### 场景一：Scenario Engine

至少消费：

- `consensus_strength`
- `dissent_width`
- `crowding_score`
- `falsification_fragility`

### 场景二：Lightweight Simulation

至少消费：

- `key_supporters`
- `key_opponents`
- `confidence_dispersion`

### 场景三：Outcome Tracker

至少消费：

- 主流共识是否兑现
- 高拥挤结构是否更易崩
- 哪类参与者构成的共识更可靠

---

## 6. 解释要求

Belief Graph 最终要能回答：

- 当前共识强不强
- 当前分歧大不大
- 这个共识是谁形成的
- 这个结构最脆弱的点在哪里
- 明天该盯什么信号验证它

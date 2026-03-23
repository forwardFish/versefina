# Market Participant Profiles 设计文档

## 1. 文档目的

本文件用于定义“市场参与者画像层”。

这是当前系统从“8 个功能 Agent”升级成“带异质性的市场参与者系统”的关键一步。

如果没有这一层，系统更像：
- 8 个分析 prompt

如果有了这一层，系统才更像：
- 一群风格不同、约束不同、反应不同的真实市场参与者

---

## 2. 为什么要有这一层

当前第一阶段的 8 类 Agent，解决的是：
- 从不同角度解释事件

但它还没解决一个更接近真实市场的问题：

**为什么同一条消息，不同资金会作出不同反应？**

比如：
- 游资可能先抢板
- 机构可能等基本面确认
- 量化可能只做短时跟随
- 风险控制型资金可能直接不参与

所以，Market Participant Profiles 的目标是：

**把“观点差异”升级成“参与者差异”。**

---

## 3. 这一层在系统里的位置

```text
第一阶段：
事件 → 8类功能 Agent → Belief Graph → 三剧本

第二阶段：
事件 → Market Participant Profiles → 参与者分歧 / 互动 → Belief Graph → 三剧本 / 小规模模拟
```

也就是说：

- 第一阶段先让系统“会分析”
- 第二阶段再让系统“像市场”

---

## 4. 画像层的核心目标

Market Participant Profiles 要回答 5 个问题：

1. 这个参与者是谁
2. 它属于哪类资金 / 风格家族
3. 它通常看重什么
4. 它在什么条件下会行动
5. 它在什么条件下会撤退

---

## 5. 参与者层级设计

### 5.1 Level 1：参与者家族（participant_family）

建议先定义最少 6 类：

1. `hot_money`：游资 / 情绪资金
2. `institutional`：机构确认型资金
3. `quant`：量化 / 模型跟随型
4. `event_driven`：事件驱动型资金
5. `defensive_capital`：防守型 / 风控优先资金
6. `content_attention`：内容 / 情绪放大型参与者

### 5.2 Level 2：风格子型（style_profile）

每个家族下再细分 1~3 个子型。

例如：

#### `hot_money`
- `fast_breakout`
- `high_conviction_leader`
- `follow_trend_chaser`

#### `institutional`
- `slow_confirmation`
- `fundamental_rerating`
- `sector_rotation`

#### `quant`
- `short_term_momentum`
- `signal_amplifier`
- `risk_off_reversal`

---

## 6. 画像字段设计

### 6.1 基础字段

| 字段 | 说明 |
|---|---|
| `participant_id` | 参与者唯一ID |
| `participant_family` | 参与者家族 |
| `style_profile` | 风格子型 |
| `display_name` | 展示名称 |
| `description` | 简介 |

### 6.2 行为字段

| 字段 | 说明 |
|---|---|
| `reaction_speed` | 反应速度 |
| `holding_preference` | 偏好的持仓周期 |
| `risk_budget_profile` | 风险预算倾向 |
| `attention_scope` | 关注范围（个股 / 板块 / 商品 / 市场） |
| `trigger_preferences` | 常见行动触发条件 |
| `exit_preferences` | 常见撤退触发条件 |
| `crowding_tolerance` | 对拥挤度容忍度 |
| `invalidation_sensitivity` | 对证伪条件敏感度 |

### 6.3 认知字段

| 字段 | 说明 |
|---|---|
| `belief_bias` | 天然偏多 / 偏空 / 中性 |
| `evidence_preference` | 更看重哪类证据 |
| `narrative_affinity` | 对叙事强弱的敏感程度 |
| `confirmation_need` | 需要多少确认信号才会行动 |
| `authority_weight` | 对权威信号重视程度 |

### 6.4 学习 / 评分字段

| 字段 | 说明 |
|---|---|
| `precision_score` | 历史判断准确度 |
| `timing_score` | 历史提前量 |
| `falsification_score` | 识别失效能力 |
| `crowding_awareness_score` | 识别拥挤风险能力 |
| `event_type_strengths` | 哪些事件类型更擅长 |

---

## 7. 画像示例

## 7.1 游资：fast_breakout

```json
{
  "participant_id": "hot_money_fast_01",
  "participant_family": "hot_money",
  "style_profile": "fast_breakout",
  "display_name": "游资-快板型",
  "reaction_speed": "very_fast",
  "holding_preference": "T+1_to_T+3",
  "risk_budget_profile": "high",
  "attention_scope": ["leader", "sector_breadth"],
  "trigger_preferences": [
    "leader_limit_up",
    "sector_volume_expansion",
    "narrative_consensus_rising"
  ],
  "exit_preferences": [
    "leader_open_board",
    "follow_stocks_fail",
    "sector_breadth_contracts"
  ],
  "crowding_tolerance": "high",
  "invalidation_sensitivity": "medium",
  "belief_bias": "bullish_if_momentum_confirms",
  "evidence_preference": ["price_action", "breadth", "market_attention"]
}
```

## 7.2 机构：slow_confirmation

```json
{
  "participant_id": "institution_slow_01",
  "participant_family": "institutional",
  "style_profile": "slow_confirmation",
  "display_name": "机构-慢确认型",
  "reaction_speed": "slow",
  "holding_preference": "T+3_to_T+20",
  "risk_budget_profile": "medium",
  "attention_scope": ["industry_logic", "earnings_quality", "valuation"],
  "trigger_preferences": [
    "causal_chain_clear",
    "multiple_confirmations",
    "institutional_peer_following"
  ],
  "exit_preferences": [
    "logic_break",
    "policy_reversal",
    "earnings_mismatch"
  ],
  "crowding_tolerance": "low_to_medium",
  "invalidation_sensitivity": "high",
  "belief_bias": "neutral_until_confirmed",
  "evidence_preference": ["fundamentals", "policy_text", "supply_chain_logic"]
}
```

---

## 8. 参与者如何接入第一阶段系统

第一阶段你不用真的让参与者模拟多轮动作。

可以先这样接：

### 第一步：把 8 类 Agent 结果映射到参与者家族
例如：
- 情绪扩散强 → 游资 / 内容参与者权重升高
- 产业链逻辑清晰 → 机构 / 事件驱动型权重升高
- 证伪条件强 → 防守型参与者权重升高

### 第二步：在 Belief Graph 中记录“是谁形成的共识”
而不只是记录“有共识”。

### 第三步：在 Scenario Engine 中输出“主导参与者组合”
比如：
- baseline 由机构 + 事件驱动形成
- bullish 由游资 + 内容放大形成
- risk 由防守型资金主导

---

## 9. 第二阶段如何升级成小规模模拟

当你接入 Simulation Runner 后，参与者就不再只是标签，而是会“行动”。

每轮最小动作建议：
- `WATCH`
- `BUILD_POSITION`
- `ADD_POSITION`
- `FOLLOW`
- `EXIT`

参与者动作由 3 类输入决定：
1. 自身 profile
2. 当前事件状态
3. 上一轮其他参与者行为

---

## 10. 与交割单的关系

交割单不是这一层的前置条件，但它是后续很重要的增强输入。

交割单接入后，可以做 3 件事：

### 10.1 风格校准
把真实交易行为抽成：
- 持仓偏好
- 加减仓节奏
- 追涨偏好
- 回撤容忍度
- 事件敏感度

### 10.2 形成 Archetype Seed
从真实交易行为抽出风格母体。

### 10.3 更新 participant scores
不是让交割单“训练大模型”，而是让它帮你校准参与者画像。

---

## 11. 数据表建议

### 11.1 participant_profiles

| 字段 | 类型 | 说明 |
|---|---|---|
| participant_id | string | 唯一ID |
| participant_family | string | 家族 |
| style_profile | string | 子型 |
| profile_json | jsonb | 全部画像字段 |
| is_active | bool | 是否启用 |

### 11.2 participant_scores

| 字段 | 类型 | 说明 |
|---|---|---|
| participant_id | string | 参与者ID |
| event_type | string | 事件类型 |
| precision_score | float | 准确度 |
| timing_score | float | 提前量 |
| falsification_score | float | 证伪能力 |
| crowding_awareness_score | float | 拥挤识别能力 |
| updated_at | datetime | 更新时间 |

### 11.3 participant_action_logs（第二阶段）

| 字段 | 类型 | 说明 |
|---|---|---|
| simulation_id | string | 模拟ID |
| round_num | int | 轮次 |
| participant_id | string | 参与者ID |
| action | string | 行为 |
| confidence | float | 当前信心 |
| reason_json | jsonb | 原因 |
| created_at | datetime | 时间 |

---

## 12. 第一阶段验收标准

第一阶段先不要求“像真人”，只要求：

1. 至少定义 6 类参与者家族
2. 每类至少 1 个主 profile
3. Belief Graph 能输出“共识由谁构成”
4. 三剧本能输出“主导参与者组合”
5. Outcome Tracker 能累计 participant scores

---

## 13. 第二阶段验收标准

第二阶段开始要求：

1. 单事件可跑 3~5 轮参与者动作
2. 每轮动作能写入 `actions.jsonl`
3. 不同风格在同一事件下会表现出差异
4. Reflection Engine 能更新 participant scores

---

## 14. 最终作用

Market Participant Profiles 的核心价值，不是让系统“更花哨”，而是让系统真正回答：

- 为什么同一条消息，不同资金反应不同
- 为什么有的题材会有人接力，有的不会
- 为什么有的共识能扩散，有的会崩
- 为什么某类风格会成为当前主导力量

一句话总结：

**没有这层，你只有“观点系统”；有了这层，你才开始拥有“市场系统”。**

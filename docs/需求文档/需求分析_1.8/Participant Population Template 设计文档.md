# Participant Population Template 设计文档

## 0. 文档定位

本文档定义 Versefina 在“8 类参与者家族”基础上，如何进一步扩展为**人口级市场参与者群体**。

目标不是让系统只有 8 个单体 Agent，而是让系统具备更贴近真实金融世界的参与者结构：

- 不同家族的人数占比不同
- 不同家族的资金体量不同
- 不同家族的传播与引导能力不同
- 同一家族内部也存在风格分化
- 参与者不是只表达观点，而是会在不同时间窗口做出买卖、加仓、减仓、广播、跟随、撤退等行为

---

## 1. 设计目标

### 1.1 核心目标

将当前 Versefina 的“8 类参与者视角输出”，升级为：

**8 个参与者家族（Participant Family）  
→ 每个家族按市场结构生成多个 Population Clone  
→ 每个 Clone 带资金体量范围、时钟偏好、仓位约束、触发规则、受影响规则与交易行为规则。**

### 1.2 为什么必须增加这一层

如果没有 Population Template 层，当前系统会停留在：

- 8 个家族级判断
- 家族级 Belief Graph
- 家族级场景推演

而无法真正逼近真实市场里：

- 散户人数更多但资金更小
- 机构人数更少但资金更大
- 游资点火强但持续性未必强
- 媒体资金不大但传播影响强
- 风控人数少但拆台能力强

### 1.3 本层解决的核心问题

1. 参与者数量如何贴近真实市场结构  
2. 参与者资金量如何分配  
3. 同一家族内部如何形成风格差异  
4. 哪类群体更容易点火、跟风、确认、拆台  
5. 如何从“家族级推演”升级为“人口级推演”

---

## 2. 当前系统现状（对接现状）

当前 Versefina 已经具备：

- 事件输入与结构化
- 参与者准备层
- Belief Graph / 场景推演 / 市场状态
- 轻量 simulation 与逐轮快照
- replay / report / validation
- `event-sandbox` 产品页
- `finahunt -> versefina` 真实事件导入与 lineage 展示

说明当前系统已经完成“事件沙盘主链”，但仍然停留在**参与者家族级原型**阶段，而不是人口级市场模拟阶段。

---

## 3. 核心概念

### 3.1 Participant Family

参与者家族。  
代表市场中的某一类典型参与者群体。

例如：

1. 散户快钱 / 情绪短线
2. 游资 / 高攻击性主动资金
3. 公募 / 机构确认型
4. 量化 / 阈值驱动型
5. 产业链确认型
6. 媒体 / 情绪扩散型
7. 风控 / 证伪型
8. 政策 / 监管解读型

### 3.2 Population Share

该类参与者在“人口数量”上的占比。

### 3.3 Capital Share

该类参与者在“资金总量”上的占比。

### 3.4 Influence Share

该类参与者在“对其他参与者的影响能力”上的占比。

### 3.5 Population Clone

参与者分身。  
是某一类 Participant Family 在某次事件模拟中的具体实例。

---

## 4. 总体原则

### 原则 1：人数占比 ≠ 资金占比 ≠ 影响占比
这三者必须分别建模，不能简单混为一谈。

### 原则 2：同一家族内部必须允许风格分化
例如散户家族内部，既有追强型，也有迟到跟风型，也有冲高撤退型。

### 原则 3：不追求复刻某一个真实机构或席位
目标是分布级逼近真实世界，而不是 1:1 复刻某个真实主体。

### 原则 4：第一阶段优先“事件驱动盘”模板
先贴近 A 股题材 / 事件驱动 / 涨价链 / 供给冲击环境。

### 原则 5：资金体量采用“范围桶”而不是精确金额
避免伪精确，提升系统稳定性与可扩展性。

---

## 5. Participant Family 定义

### 5.1 Family 1：散户快钱 / 情绪短线

#### 作用
- 数量最多
- 更容易被强势龙头、热度、媒体叙事带动
- 易点火跟风，也易快速撤退

#### 建议风格变体
- `RetailFast_LeaderSensitive`
- `RetailFast_TrendChaser`
- `RetailFast_LateFollower`

#### 典型行为
- 早盘追强
- 看见首板或龙头强势后跟进
- 对媒体情绪和板块热度敏感
- 失效后撤退也快

---

### 5.2 Family 2：游资 / 高攻击性主动资金

#### 作用
- 点火能力最强
- 数量不多，但对短期方向决定性强
- 会带动快钱和跟风群体

#### 建议风格变体
- `HotMoney_FastBreakout`
- `HotMoney_HighConvictionLeader`
- `HotMoney_TacticalExit`

#### 典型行为
- 更容易在高辨识度龙头上率先试仓或进攻
- 确认后可迅速拉高事件热度
- 若失败则快速撤退

---

### 5.3 Family 3：公募 / 机构确认型

#### 作用
- 数量少
- 单体资金大
- 更晚确认，但一旦进入会提升主线持续性

#### 建议风格变体
- `Institution_SlowConfirmation`
- `Institution_ReRatingBuilder`
- `Institution_DefensiveAllocator`

#### 典型行为
- 依赖产业链可持续验证
- 不会最先点火
- 更重视确认信号和中短期持续性

---

### 5.4 Family 4：量化 / 阈值驱动型

#### 作用
- 不一定负责讲故事
- 但会在阈值满足时参与放大
- 风险信号变差时撤退快

#### 建议风格变体
- `Quant_ThresholdFollower`
- `Quant_VolatilityReducer`
- `Quant_TrendModel`

---

### 5.5 Family 5：产业链确认型

#### 作用
- 负责验证事件是否会沿链条传导
- 对机构确认型、慢钱极其重要

#### 建议风格变体
- `ChainExpert_Validator`
- `ChainExpert_LinkageMapper`

---

### 5.6 Family 6：媒体 / 情绪扩散型

#### 作用
- 不一定资金最大
- 但对传播和叙事形成非常重要

#### 建议风格变体
- `Media_NarrativeAmplifier`
- `Media_HeatExpander`
- `Media_SkepticVoice`

---

### 5.7 Family 7：风控 / 证伪型

#### 作用
- 负责识别拥挤、脆弱性和证伪条件
- 对失败链形成关键影响

#### 建议风格变体
- `Risk_FragilityDetector`
- `Risk_OvercrowdingAlarm`
- `Risk_InvalidationWatcher`

---

### 5.8 Family 8：政策 / 监管解读型

#### 作用
- 对“涨价链 / 供给冲击”首发阶段不是最核心
- 但对后续持续性解释仍有作用

#### 建议风格变体
- `Policy_InterpretiveBull`
- `Policy_CautionReader`

---

## 6. 市场结构模板（Population Template）

### 6.1 为什么要有模板

同一套参与者家族，在不同市场环境下：
- 人数分布不同
- 资金分布不同
- 影响分布不同

因此需要一个“市场结构模板”。

### 6.2 模板 A：A股题材 / 事件驱动盘（首发推荐）

| Family | population_share | capital_share | influence_share | default_clone_count |
|---|---:|---:|---:|---:|
| 散户快钱 | 0.35 | 0.15 | 0.18 | 8 |
| 游资 | 0.08 | 0.18 | 0.25 | 2 |
| 公募 / 机构确认型 | 0.05 | 0.28 | 0.18 | 1 |
| 量化 | 0.08 | 0.16 | 0.10 | 2 |
| 产业链确认型 | 0.08 | 0.05 | 0.12 | 2 |
| 媒体 / 情绪扩散型 | 0.16 | 0.03 | 0.10 | 4 |
| 风控 / 证伪型 | 0.10 | 0.08 | 0.05 | 3 |
| 政策 / 监管解读型 | 0.10 | 0.07 | 0.02 | 2 |

说明：
- 数量最多的不是资金最多的
- 影响力最强的未必人数最多
- 资金最厚的未必最先行动

### 6.3 模板 B：机构主导盘（预留）
暂不在首阶段启用，但保留：
- 机构资本份额更高
- 媒体与散户权重下降
- 量化与风控更重要

### 6.4 模板 C：突发风险盘（预留）
暂不在首阶段启用，但保留：
- 风控与媒体权重提升
- 跟风与扩散缩短
- 失效边更强

---

## 7. Clone 生成规则

### 7.1 输入

- `event_type`
- `market_regime`
- `market_template_id`
- `base_population_size`

### 7.2 输出

- `PopulationRoster`

### 7.3 生成逻辑

#### Step 1：选择模板
根据市场 regime 选择对应的 `ParticipantPopulationTemplate`。

#### Step 2：计算家族 clone 数量
推荐公式：

```text
clone_count = round(population_share * base_population_size)
```

建议首发：
- `base_population_size = 24`

#### Step 3：为每个 clone 采样风格变体
从该 family 的 style variants 中按权重抽样。

#### Step 4：为每个 clone 采样资金桶
从 family 对应的 capital buckets 中抽样。

#### Step 5：生成个体级规则
为每个 clone 生成：
- 反应延迟
- 入场阈值
- 加仓阈值
- 退出阈值
- 影响权重
- 当前现金与持仓状态

---

## 8. Capital Bucket 设计

### 8.1 散户快钱

#### 资金桶
- `5w ~ 20w`
- `20w ~ 80w`
- `80w ~ 300w`

#### 风险上限
- `max_event_exposure = 10% ~ 35%`
- `max_symbol_exposure = 5% ~ 20%`

---

### 8.2 游资

#### 资金桶
- `300w ~ 1000w`
- `1000w ~ 5000w`
- `5000w ~ 2e`

#### 风险上限
- `max_event_exposure = 20% ~ 50%`
- `max_symbol_exposure = 10% ~ 35%`

---

### 8.3 公募 / 机构确认型

#### 资金桶
- `3000w ~ 1e`
- `1e ~ 5e`
- `5e ~ 20e`

#### 风险上限
- `max_event_exposure = 5% ~ 20%`
- `max_symbol_exposure = 3% ~ 12%`

---

### 8.4 量化

#### 资金桶
- `1000w ~ 5000w`
- `5000w ~ 2e`

#### 风险上限
- `max_event_exposure = 8% ~ 18%`
- `max_symbol_exposure = 4% ~ 10%`

---

### 8.5 产业链确认型
这类角色资金中等，可偏研究驱动。
建议作为中等资金桶处理：
- `500w ~ 3000w`
- `3000w ~ 1e`

---

### 8.6 媒体 / 情绪扩散型
可以资金较低甚至接近零仓位，但传播权重高。

---

### 8.7 风控 / 证伪型
资金不必最大，但应具备较高 suppress 权重和较高退出触发敏感度。

---

## 9. Clone 级字段定义

每个 Population Clone 至少包括以下字段：

- `clone_id`
- `participant_family`
- `style_variant`
- `population_weight`
- `capital_bucket`
- `cash_available`
- `max_event_exposure`
- `max_symbol_exposure`
- `reaction_latency`
- `entry_threshold`
- `add_threshold`
- `reduce_threshold`
- `exit_threshold`
- `authority_weight`
- `influence_weight`
- `risk_budget_profile`
- `current_position`
- `current_state`

---

## 10. 行为规则层（Population 层必带）

每个 clone 必须具有：

### 10.1 事件触发规则
- 哪类消息会激活自己
- 何种 source quality 下更敏感
- 哪些 commodity / sector 会优先关注

### 10.2 行为触发规则
- 龙头强度达到阈值
- 板块 breadth 扩大
- 同链条二线出现
- 产业链确认增强

### 10.3 退出规则
- 龙头高开低走
- 价格回吐
- 扩散失败
- 风控信号增强

### 10.4 受影响规则
- 被哪些 family 影响最大
- 哪种影响边会改变其买卖概率

### 10.5 时钟规则
- 更偏 `pre_open`
- 更偏 `open_5m`
- 更偏 `morning_30m`
- 更偏 `midday_reprice`
- 更偏 `afternoon_follow`
- 更偏 `close_positioning`

---

## 11. 与当前 Versefina 的对接方式

当前 Versefina 已经具备：
- 事件输入与结构化
- 参与者准备层
- Belief Graph / 场景推演 / 市场状态
- 轻量 simulation 与逐轮快照
- replay / report / validation
- 真实事件导入与 lineage 展示

因此 Population Template 层不需要推翻现有系统，而应作为当前 `participants/prepare` 的增强层接入。

### 当前对接建议

旧流程：

```text
事件结构化
→ 8 类参与者准备
→ Belief Graph
```

新流程：

```text
事件结构化
→ Population Template 选择
→ Population Roster 生成
→ Clone 级参与者准备
→ 家族级聚合
→ Belief Graph
```

---

## 12. 对下游模块的影响

Population 层引入后，将影响：

### 12.1 Belief Graph
Belief 不再只来自 8 个 family，而来自：
- Clone 级行为
- 再聚合到 family
- 再聚合到 market

### 12.2 Simulation
动作不再只是家族级观点，而是 clone 级买卖与传播。

### 12.3 Replay
Replay 不再只是“哪类参与者如何看”，而是“哪一群、哪几个 clone 如何行动”。

### 12.4 Validation
Validation 可以统计：
- 哪类 family 更可靠
- 哪类 clone 结构更常 lead
- 哪类人口组合更容易导致 crowding / invalidation

---

## 13. 第一阶段验收标准

### 验收 1
至少实现模板 A：A股题材 / 事件驱动盘。

### 验收 2
至少支持 `base_population_size = 24` 的 clone 生成。

### 验收 3
每个 clone 均具备：
- style_variant
- capital_bucket
- reaction_latency
- event/symbol exposure 限制

### 验收 4
页面可以看到：
- family 数量
- clone 数量
- 各 family 大致资金权重
- 各 family 大致影响权重

### 验收 5
replay 中能看到：
- 某些 clone 先动
- 某些 clone 跟随
- 某些 clone 退出

---

## 14. 下一步配套文档

1. `Population_Generator_Rules.md`
2. `Capital_Bucket_and_Position_Rules.md`
3. `Execution_Action_Protocol_V2.md`
4. `Influence_to_Trade_Conversion.md`
5. `Population_Visualization_UI.md`

---

## 15. 一句话总结

**Participant Population Template 的目标，是把 Versefina 从“8 类家族级参与者沙盘”，升级成“带人口分布、资金分布、影响分布的缩小版金融市场”。**

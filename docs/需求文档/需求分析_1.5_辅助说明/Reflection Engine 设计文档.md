# Reflection Engine 设计文档

## 1. 文档目的

Reflection Engine 的目标很简单：

**不是只让系统“跑一次”，而是让系统在跑完后知道自己哪里对、哪里错，并逐步修正。**

这是借鉴 TradingAgents 最值得学的一层。

---

## 2. Reflection Engine 解决什么问题

如果没有 Reflection Engine，系统会出现 4 个问题：

1. 每次都重新开始，无法积累经验
2. 不知道哪类 Agent 在什么场景更可靠
3. 不知道哪类剧本结构更容易命中
4. 不知道哪类失效条件最常提前触发

所以 Outcome Tracker 不是终点，**Reflection Engine 才是让系统变强的开始。**

---

## 3. 输入与输出

### 3.1 输入

Reflection Engine 至少要读取这 5 类数据：

1. `event_structure`
2. `agent_outputs`
3. `belief_graph_snapshot`
4. `scenario_result`
5. `outcome_tracker_result`

### 3.2 输出

Reflection Engine 的输出不直接给用户，而是写回系统：

- 参与者可靠度分数更新
- 事件类型先验更新
- 剧本模板权重更新
- 失败模式库更新
- 规则阈值微调建议

---

## 4. 核心目标

Reflection Engine 要完成 4 件事：

### 4.1 评估谁更准
比如：
- 哪类 Agent 在涨价链事件里更准
- 哪类参与者在情绪扩散里更准
- 哪种风格最容易提前判断失效

### 4.2 评估哪种共识结构更有效
比如：
- 高共识 + 低分歧是否更容易兑现
- 高拥挤是否更容易失败
- 高信心分散是否意味着风险更高

### 4.3 评估剧本模板是否需要调整
比如：
- 当前 baseline 总是太保守
- bullish 总是过度乐观
- risk scenario 经常漏掉某类失败路径

### 4.4 形成长期失败模式库
比如：
- 题材未扩散，因为中游标的承接不足
- 题材失败，因为市场风格不支持高位接力
- 题材失效，因为证伪条件比预期更早触发

---

## 5. 设计原则

### 原则 1：先从规则型开始，不要一开始就做复杂学习
第一版 Reflection Engine 用规则就够：
- 命中 / 半命中 / 失败
- 提前量高 / 中 / 低
- 失效触发早 / 晚

### 原则 2：先做“统计反思”，再做“模型反思”
第一阶段先统计：
- 命中率
- 失效率
- 提前量
- 风险漏检率

第二阶段再加 LLM 生成的解释性复盘。

### 原则 3：反思结果先写给系统，不直接变用户展示
避免系统变成“写好听复盘”的样子。

---

## 6. 数据结构建议

### 6.1 reflection_records

| 字段 | 类型 | 说明 |
|---|---|---|
| id | string | 反思记录ID |
| event_id | string | 关联事件 |
| reflection_time | datetime | 反思时间 |
| event_type | string | 事件类型 |
| dominant_scenario | string | 当时主剧本 |
| outcome_label | string | 命中 / 半命中 / 失败 |
| latency_score | float | 提前量分数 |
| reflection_summary | jsonb | 反思摘要 |

### 6.2 participant_reflection_scores

| 字段 | 类型 | 说明 |
|---|---|---|
| participant_id | string | 参与者ID |
| event_type | string | 事件类型 |
| precision_score | float | 准确度 |
| timing_score | float | 时点判断 |
| falsification_score | float | 证伪能力 |
| crowding_awareness_score | float | 拥挤识别能力 |
| updated_at | datetime | 更新时间 |

### 6.3 failure_pattern_library

| 字段 | 类型 | 说明 |
|---|---|---|
| id | string | 模式ID |
| event_type | string | 事件类型 |
| pattern_name | string | 模式名称 |
| trigger_signature | jsonb | 触发特征 |
| observed_outcomes | jsonb | 结果摘要 |
| confidence | float | 置信度 |

---

## 7. 核心流程

```text
Outcome Tracker 完成
→ 读取事件与剧本快照
→ 对比真实结果
→ 计算命中 / 半命中 / 失败
→ 评估各参与者贡献
→ 更新事件类型先验
→ 更新失败模式库
→ 产出 reflection_summary
```

---

## 8. 反思层级

### 8.1 Agent 级反思
问题：
- 哪个 Agent 经常过度乐观？
- 哪个 Agent 经常太保守？
- 哪个 Agent 更擅长找失效点？

### 8.2 Participant 家族级反思
问题：
- 游资型参与者在哪类事件更有效？
- 机构确认型参与者在哪类事件更有效？
- 量化防守型参与者在哪类环境更容易提前撤退？

### 8.3 Belief Graph 级反思
问题：
- 高共识是否真有用？
- 高拥挤是否真危险？
- 分歧越大是不是越容易失败？

### 8.4 Scenario 模板级反思
问题：
- baseline 是否总是偏弱？
- risk scenario 是否漏掉了关键断点？
- bullish 是否需要更严格的触发条件？

---

## 9. 第一阶段建议实现的规则

第一阶段只做 6 条最实用规则：

1. **命中则提高主导参与者得分**
2. **失败则降低主导参与者得分**
3. **提前量高则额外加分**
4. **失效条件提前触发则提高 falsification score**
5. **高拥挤但未崩，则 crowding 权重下降一点**
6. **连续多次出现相似失败路径，则加入失败模式库**

---

## 10. 第二阶段可以增强的内容

### 10.1 LLM 复盘摘要
自动总结：
- 当时为什么会这样判断
- 实际为什么没有兑现
- 系统接下来该改什么

### 10.2 动态阈值调整
比如：
- baseline 权重
- crowding 阈值
- falsification 触发阈值

### 10.3 事件类型特定反思
不同事件类型分开统计，不要混在一起。

---

## 11. 接口建议

### `run_reflection(event_id: str)`
功能：
- 针对单个事件做反思

### `update_participant_scores(reflection_result)`
功能：
- 更新参与者可靠度

### `update_failure_patterns(reflection_result)`
功能：
- 更新失败模式库

### `generate_reflection_summary(reflection_result)`
功能：
- 生成可读摘要

---

## 12. 验收标准

### 第一阶段验收
- 能对每条完成验证的事件生成 reflection record
- 能更新 participant scores
- 能记录至少 3 类失败模式
- 能输出一段简短 reflection summary

### 第二阶段验收
- 能按事件类型分类反思
- 能识别“哪类参与者在哪类环境更有效”
- 能用于下一轮 Scenario Engine 权重微调

---

## 13. 最终作用

Reflection Engine 的价值，不是“让系统看起来会学习”，而是让系统真正形成以下能力：

- 越跑越知道谁靠谱
- 越跑越知道哪种共识会崩
- 越跑越知道哪种失效最常见
- 越跑越知道剧本怎么调得更稳

一句话总结：

**Outcome Tracker 告诉你发生了什么，Reflection Engine 告诉你下次该怎么做得更好。**

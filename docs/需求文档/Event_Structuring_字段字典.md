# Event Structuring 字段字典

## 1. 目标

本字典定义 `EventStructure` 的稳定字段，要求输出结果可被：

- Participant Preparation
- Belief Graph
- Scenario Engine
- Outcome Tracker

共同消费。

---

## 2. 顶层对象

### `event_id`
- 类型：`string`
- 说明：事件唯一标识

### `event_type`
- 类型：`string`
- 说明：当前阶段固定为 `supply_chain_price_shock`

### `event_time`
- 类型：`datetime string`
- 说明：事件原始发生时间

### `summary`
- 类型：`string`
- 说明：面向系统内部的短摘要，不超过 200 字

---

## 3. 结构化字段

### `entities`
- 类型：`array`
- 说明：事件直接涉及的公司、机构、商品、地区、装置、港口等实体

### `commodities`
- 类型：`array`
- 说明：受影响的核心商品列表

### `chain_links`
- 类型：`array`
- 说明：产业链环节，如上游 / 中游 / 下游

### `sectors`
- 类型：`array`
- 说明：映射到的行业或题材板块

### `affected_symbols`
- 类型：`array`
- 说明：第一轮受影响的 A 股标的池

### `causal_chain`
- 类型：`array`
- 说明：从事件到商品、行业、标的的因果链条

---

## 4. 观察与失效字段

### `monitor_signals`
- 类型：`array`
- 说明：次日或未来几日需要重点观察的确认信号

必含维度：

- 价格确认
- 量能确认
- 龙头确认
- 板块扩散确认
- 机构跟随确认

### `invalidation_conditions`
- 类型：`array`
- 说明：剧本失效条件

必含维度：

- 价格未兑现
- 龙头转弱
- 分歧急剧扩大
- 关键参与者缺位
- 传导链被截断

---

## 5. 建议输出样例

```json
{
  "event_id": "evt_20260323_001",
  "event_type": "supply_chain_price_shock",
  "entities": ["某化工品", "某停产工厂"],
  "commodities": ["化工原料A"],
  "chain_links": ["上游", "中游"],
  "sectors": ["化工", "新材料"],
  "affected_symbols": ["000001.SZ", "000002.SZ"],
  "causal_chain": [
    "停产导致供给下降",
    "供给下降导致原料涨价",
    "原料涨价向中游成本传导"
  ],
  "monitor_signals": [
    "次日原料现货价格继续上行",
    "龙头标的放量强势"
  ],
  "invalidation_conditions": [
    "价格冲高回落且量能不足",
    "龙头失去封板或高开低走"
  ]
}
```

---

## 6. 输出约束

- 不允许只返回大段自由文本
- 必须保证字段齐全、结构稳定
- 缺失信息时允许字段为空数组，但必须保留字段本身
- 结构化结果必须可复跑、可追踪、可比较

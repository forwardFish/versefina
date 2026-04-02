# 需求分析_终局完整版_Codex直开发.md

## 文档定位

本文档是 Versefina 的**终局完整版需求文档**。

它不是阶段路线图，不讨论“先做 1 再做 2 再做 3”。  
它直接定义：

- 最终产品是什么
- 最终系统必须包含什么
- 最终页面必须长什么样
- 最终参与者如何被触发、如何互相影响、如何买卖
- 最终图谱如何驱动系统
- 最终报告、验证、深度互动必须做到什么程度
- Codex 按这份文档持续开发，直到系统达到这里描述的终局状态

---

# 1. 最终产品定义

Versefina 的最终产品不是“消息分析器”，不是“荐股器”，也不是“单次观点生成器”。

Versefina 的最终产品是：

**一个金融事件驱动的、图谱驱动的、人口级市场参与者交易演化系统。**

它要做到：

一条金融消息进入系统后，系统会先构建事件图谱，再根据市场状态和参与者模板，生成不同类型的市场参与者分身；这些参与者分身带着各自的资金体量范围、仓位约束、交易风格、反应延迟、确认规则、退出规则，在多个交易时间窗口中真实地做出买入、加仓、减仓、退出、传播、确认、压制等动作；这些动作通过影响图相互作用，持续改变 Belief Graph 和 Market State，最终演化出一个更接近真实金融世界的市场过程。系统不仅要展示结果，还要展示过程、解释原因、支持追问、支持反事实推演、支持后验验证与持续校准。

---

# 2. 最终产品不是做什么

Versefina 最终版不是：

- 自动实盘下单系统
- 券商接入系统
- 高频撮合引擎
- 单纯的新闻总结器
- 单纯的题材推荐器
- 靠基础大模型一次性猜结果的黑箱系统
- 逐笔逐席位完全复刻真实市场的系统

Versefina 最终版要追求的是：

**分布级、结构级、过程级逼近真实金融世界。**

也就是：
- 参与者结构尽量像真实市场
- 资金分布尽量像真实市场
- 传播路径尽量像真实市场
- 交易节奏尽量像真实市场
- 成功与失败链条尽量像真实市场

---

# 3. 最终系统要回答的核心问题

最终系统必须能回答：

1. 这条消息是什么事件？
2. 它影响哪条产业链、哪些商品、哪些板块、哪些标的？
3. 哪些参与者会最先被激活？
4. 哪些参与者只是 watch，哪些会直接 lead？
5. 每个参与者在什么时间窗口买入、买多少范围、为什么买？
6. 哪些参与者会跟随？哪些参与者会确认？哪些参与者会压制？
7. 谁影响了谁？这条影响边为什么成立？
8. 市场状态是如何从 dormant 进入 ignition，再进入 propagating / crowded / fragile / invalidated？
9. 最终主导剧本为什么成立？
10. 为什么失败？失败链条是什么？
11. 如果条件改变，结果会不会改变？
12. T+1 / T+3 / T+N 后验证结果如何？
13. 哪类参与者更可靠？哪类结构更容易失效？
14. 在不同市场环境下，这类事件通常会如何演化？

---

# 4. 最终系统的四层核心图谱

Versefina 的最终内核必须是四层图谱，而不是一堆互相独立的表和页面。

## 4.1 Event Graph（事件图谱）

Event Graph 用于表示一条消息本身的结构。

### 必须包含的节点
- Event
- Commodity
- Sector
- Symbol
- ConfirmationSignal
- InvalidationSignal
- RiskFactor
- SentimentSeed

### 必须包含的边
- impacts
- propagates_to
- confirms
- invalidates
- linked_to
- depends_on
- amplifies
- weakens

### 必须解决的问题
- 消息属于哪类事件
- 冲击从哪里产生
- 会沿着哪条链条传导
- 哪些信号证明它成立
- 哪些信号证明它失效

---

## 4.2 Participant Graph（参与者图谱）

Participant Graph 用于表示不同市场参与者家族与其分身。

### 必须包含的对象
- Participant Family
- Population Template
- Population Clone
- Clone State
- Clone Capital Profile
- Clone Style Variant
- Clone Risk Budget

### 参与者家族必须至少包括
1. 散户快钱 / 情绪短线
2. 游资 / 高攻击性主动资金
3. 公募 / 机构确认型
4. 量化 / 阈值驱动型
5. 产业链确认型
6. 媒体 / 情绪扩散型
7. 风控 / 证伪型
8. 政策 / 监管解读型

### 每个家族必须不是单体，而是 Population
即：
- 有人数占比
- 有资金占比
- 有影响占比
- 有多个 clone
- 同一家族内部允许风格分化

---

## 4.3 Influence Graph（影响图谱）

Influence Graph 用于表示参与者之间是如何互相影响的。

### 必须支持的边类型
- LEADS
- FOLLOWS
- CONFIRMS
- QUESTIONS
- AMPLIFIES
- SUPPRESSES
- ROTATES
- INVALIDATES

### 每条影响边必须具备
- source
- target
- influence_type
- effect_type
- effect_strength
- lag_rounds
- activation_condition
- expiration_condition
- evidence_trace

### 影响边不能只是展示
它必须真正改变：
- entry probability
- add probability
- follow probability
- reduce probability
- exit probability
- confidence
- crowding
- fragility

---

## 4.4 Market State Graph（市场状态图谱）

Market State Graph 用于表示市场整体演化到了哪里。

### 必须支持的状态
- Dormant
- Ignition
- Propagating
- Crowded
- Fragile
- Invalidated

### 每个状态迁移必须有清晰条件
例如：
- DORMANT → IGNITION
- IGNITION → PROPAGATING
- PROPAGATING → CROWDED
- PROPAGATING → FRAGILE
- CROWDED → INVALIDATED
- FRAGILE → INVALIDATED

### 状态迁移必须由真实模拟信号驱动
不能只靠 prompt 口头判断。

必须至少综合：
- 净买力近似
- clone lead / follow / reduce / exit 行为占比
- breadth 扩散近似
- 确认信号强度
- 证伪信号强度
- crowding_score
- falsification_fragility

---

# 5. 最终参与者模型

## 5.1 8 个 Agent 不是 8 个角色，而是 8 个家族

每个家族下面必须生成多个 clone。

### 必须区分三种权重
- 人口占比（population_share）
- 资金占比（capital_share）
- 影响占比（influence_share）

这三者必须独立存在，不能混为一谈。

---

## 5.2 每个 clone 必须具备的字段

### 身份字段
- clone_id
- family_id
- style_variant
- description

### 资金字段
- capital_bucket_min
- capital_bucket_max
- cash_available_min
- cash_available_max
- max_event_exposure_min
- max_event_exposure_max
- max_symbol_exposure_min
- max_symbol_exposure_max

### 状态字段
- current_state
- current_position_summary
- current_cash_summary
- current_confidence
- current_attention_level

### 行为字段
- reaction_latency
- entry_threshold
- add_threshold
- reduce_threshold
- exit_threshold
- authority_weight
- influence_weight
- risk_budget_profile

### 时钟字段
- preferred_execution_windows
- avoid_execution_windows

### 规则字段
- activation_rules
- confirmation_rules
- invalidation_rules
- follow_rules
- suppression_rules
- exit_rules

---

## 5.3 人口模板必须支持的真实市场近似

最终系统必须至少内建如下模板：

### 模板 A：A股题材 / 事件驱动盘
最优先支持。

### 模板 B：机构主导盘
适用于慢钱主导 / 确认更慢的市场环境。

### 模板 C：突发风险盘
适用于负面事件、风控权重提升、扩散更短的环境。

### 模板 D：情绪极热盘
适用于散户 / 游资 / 媒体占优、拥挤更快到来的环境。

每个模板都要定义：
- base_population_size
- family_allocations
- style_distribution
- capital_distribution
- influence_distribution

---

# 6. 最终交易行为模型

最终系统不能停留在 WATCH / VALIDATE 这种“观点动作”层。

最终系统必须支持交易动作。

## 6.1 最低要求动作集

- WATCH
- VALIDATE
- INIT_BUY
- ADD_BUY
- REDUCE
- EXIT
- BROADCAST_BULL
- BROADCAST_BEAR

## 6.2 每个动作必须记录

- action_id
- simulation_id
- round_no
- execution_window
- clone_id
- action_type
- target_symbol
- target_theme
- order_side
- order_style
- order_size_pct
- order_value_range_min
- order_value_range_max
- position_before
- position_after
- cash_before
- cash_after
- influenced_by
- reason_codes
- market_state_before
- market_state_after

## 6.3 动作必须和真实金融世界相似

### INIT_BUY
首次试仓  
不是重仓打满。

### ADD_BUY
确认后加仓  
必须依赖确认信号或外部强化。

### REDUCE
减仓  
用于拥挤加剧、强度转弱、风险上升。

### EXIT
退出  
用于失效或被风险信号压制。

### BROADCAST_BULL / BEAR
不一定直接带来交易，但必须影响其他 clone 的买卖概率。

---

# 7. 最终执行时钟

最终系统不能只用抽象 round。

必须具备更像真实市场的交易窗口。

## 必须支持的执行窗口
- pre_open
- open_5m
- morning_30m
- midday_reprice
- afternoon_follow
- close_positioning

## 不同家族的典型偏好
### 游资
偏早盘，尤其 open_5m / morning_30m

### 散户快钱
偏 morning_30m / afternoon_follow

### 机构确认型
偏 midday_reprice / close_positioning

### 风控
各窗口都可能触发，但对后段更敏感

### 媒体 / 扩散型
跨窗口广播

---

# 8. 最终模拟机制

最终系统必须是一个真实的“交易行为模拟系统”，而不是一个多代理写作文系统。

## 8.1 单事件模拟必须包含

1. Event Graph 构建
2. Population Template 选择
3. Population Generator 生成 clone roster
4. Clone 初始化（资金、阈值、时钟、状态）
5. 逐窗口 / 逐轮模拟
6. Influence-to-Trade 生效
7. Belief Graph 更新
8. Market State 更新
9. Scenario 动态修正
10. Replay / Report / Validation

---

## 8.2 模拟过程必须发生的事情

### 第一层
谁被触发

### 第二层
谁先下手

### 第三层
谁跟随，谁确认，谁压制

### 第四层
市场状态如何变化

### 第五层
最终主导剧本是什么

### 第六层
为什么成功 / 为什么失败

---

# 9. 最终页面形态

最终页面不是多个 tab 拼起来，而是一张：

**单事件演化墙**

## 页面必须包含四个主区块

### 左侧：Event Graph + lineage
显示：
- 原始消息
- 结构化结果
- commodity / sector / symbol
- causal_chain
- confirmation signals
- invalidation conditions
- 来源 lineage
- finahunt 来源上下文

### 中央：Population & Interaction Stage
显示：
- 当前 round / 当前 execution window
- 当前活跃 clone
- 谁正在 lead / follow / reduce / exit
- influence edges
- 当前 dominant participants
- 当前 market state

### 右侧：Belief / Scenario / MarketState
显示：
- consensus_strength
- dissent_width
- crowding_score
- falsification_fragility
- dominant_scenario
- bull/base/bear
- next_watchpoints
- key_support_chain
- key_opposition_chain

### 底部：Replay Timeline
显示：
- pre_open
- open_5m
- morning_30m
- midday_reprice
- afternoon_follow
- close_positioning

每个时间窗口点击后，都要能看到：
- 谁动了
- 做了什么动作
- 影响了谁
- 当前 market state 变成什么

---

## 9.1 页面必须支持的点击行为

### 点击某个 clone
必须看到：
- 家族
- 风格
- 资金范围
- 仓位范围
- 行为阈值
- 本轮动作
- 影响了谁
- 被谁影响

### 点击某条 influence edge
必须看到：
- 这条边为什么被激活
- 这条边如何改变了对方的买卖概率
- 这条边何时失效
- 有哪些 evidence_trace

### 点击某个剧本
必须看到：
- 这个剧本为何成为 dominant
- 哪些链条支持它
- 哪些链条反对它
- 哪些失效条件最关键

### 点击某个市场状态迁移点
必须看到：
- 为什么从 A 状态变成 B 状态
- 哪些 clone 动作最关键
- 哪些边最关键

---

# 10. 最终报告系统

最终报告不能只是摘要。

必须形成 5 类报告。

## 10.1 事件图谱报告
说明：
- 事件结构
- 传导链
- 确认点
- 失效点

## 10.2 人口级交易行为报告
说明：
- 哪些家族 / clone 被激活
- 资金体量大致如何进入
- 何时买 / 加 / 减 / 退

## 10.3 成功 / 失败 / 脆弱链报告
说明：
- 哪条链推动成功
- 哪条链导致失败
- 哪条链构成脆弱性

## 10.4 剧本演化报告
说明：
- bull/base/bear 如何随着轮次变化
- 为什么最终 dominant scenario 定格在当前结果

## 10.5 验证与可靠性报告
说明：
- T+1 / T+3 / T+N 回填
- family reliability
- clone reliability
- failure taxonomy
- regime-specific pattern

---

# 11. 最终深度互动系统

最终系统必须具备强互动能力，不只是看结果。

## 用户必须可以问的问题
- 为什么这个 clone 会先买？
- 为什么机构没有跟？
- 为什么媒体放大后快钱先动了？
- 为什么从 Propagating 变成了 Fragile？
- 如果龙头没有回落，会不会继续扩散？
- 如果再来一条政策消息，会不会改变结果？
- 哪类群体在这类事件里最常 lead？
- 这次失败是因为哪个链条断了？

## 深度互动必须引用真实过程
不能只用大模型空讲。  
必须引用：
- graph
- replay
- scenario
- validation
- evidence trace

---

# 12. 最终验证系统

最终系统必须具备强 validation，不是只验证“这次对不对”。

## 必须验证的层
- event level
- scenario level
- family level
- clone level
- regime level

## 必须统计的内容
- hit
- partial_hit
- delayed_realization
- invalidated
- wrong_direction

## 必须形成的视图
- family reliability scoreboard
- clone reliability scoreboard
- failure taxonomy board
- regime pattern board

---

# 13. 最终还需要的更高层能力

即使单事件沙盘和验证闭环都完成，最终系统还要支持更强能力。

## 13.1 跨事件市场上下文
系统不能永远把每条消息当成独立世界。

必须支持：
- 当前主线
- 旧主线残留
- 跨事件仓位占用
- 多事件冲突
- 市场整体风险温度

## 13.2 反事实推演
最终系统应支持：
- 如果条件 A 改变，会怎样
- 如果龙头继续强，会怎样
- 如果明天再来一条相关消息，会怎样
- 如果风控信号先出现，会怎样

## 13.3 自校准能力
最终系统应支持：
- population template 校准
- influence rule 校准
- 不同 regime 下规则自动调整

---

# 14. Codex 最终开发要求

Codex 不应只把这份文档理解成“需求描述”，而应理解成：

**最终产品形态的唯一权威定义。**

Codex 开发时必须遵守：

1. 不推翻当前 Versefina 主链
2. 先在现有系统上增强
3. 所有新增能力必须能在 event-sandbox 中被看见
4. 所有新增动作必须有日志
5. 所有新增边必须能解释
6. 所有新增状态迁移必须能追踪原因
7. 所有新增页面能力必须支持点击追问
8. 所有新增验证能力必须进入 scoreboard
9. 每次提交必须同步更新：
   - 代码
   - migration
   - API 说明
   - 页面说明
   - 验收结果
   - 未完成项
   - 风险说明

---

# 15. 实际开发顺序要求

虽然这份文档不是阶段路线图文档，但 Codex 在实际开发时必须默认遵守如下顺序：

### 必须先完成
- Population Template
- Population Generator
- Clone Roster
- Capital Buckets
- Execution Clock
- ExecutionActionV2

### 然后完成
- Influence-to-Trade
- MarketStateEngineV2
- event-sandbox 单事件演化墙增强

### 然后完成
- Replay / Report / Validation V2
- family / clone scoreboard
- failure taxonomy

### 最后完成
- 跨事件市场上下文
- 反事实推演
- 自校准系统
- 终局版深度互动

---

# 16. 最终验收标准

Versefina 终局版完成时，必须满足：

## 16.1 产品层
- 用户打开 event-sandbox，就能看到一个“市场在动”
- 用户能清晰看到谁先被触发、谁买了、买多少范围、谁跟随、谁退出
- 用户能看到 market state 是如何演化的

## 16.2 模型层
- family / clone / graph / state 四层对象统一
- influence graph 不只是展示，而是真正改变交易行为
- scenario 会随着模拟变化

## 16.3 报告层
- 可以输出成功链 / 失败链 / 脆弱链
- 可以输出 family / clone 可靠性
- 可以输出 regime-specific pattern

## 16.4 互动层
- 用户点击 clone / edge / scenario / state transition 都能追问
- 系统回答必须引用真实 replay 和 graph 证据

## 16.5 工程层
- 代码、页面、API、文档、治理状态一致
- roadmap、registry、acceptance、README、demo 全对齐

---

# 17. 一句话总结

**Versefina 的终局，不是把 8 个 Agent 做得更复杂，而是把它真正做成一个“带图谱、带人口分布、带交易行为、带市场状态演化、带解释与验证、带深度互动”的金融事件演化系统。**

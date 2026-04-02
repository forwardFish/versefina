# Versefina 项目最终总结

更新时间：2026-04-02

## 1. 文档目的

这份文档用于给 `Versefina` 当前项目状态做一次完整收束，回答 5 个问题：

1. `Versefina` 现在到底已经做成了什么
2. `roadmap_1_6`、`roadmap_1_7`、`roadmap_1_8`、`roadmap_1_9` 之间是什么递进关系
3. 当前代码、页面、接口、验证面分别落在什么完成边界
4. 目前哪些能力已经可用，哪些问题仍然属于待收口事项
5. 如果继续推进，下一阶段最值得做的是什么

这份总结不是单独复述某一轮 Story，而是将历史报告、当前代码结构、最新 workbench 交付结果合并成一份面向整个项目的总账本。

## 2. 结论先行

一句话结论：

**Versefina 当前已经从早期的事件理解与轻量推演原型，发展为一个可接收事件、激活参与者与 clone、形成影响链、执行多轮或多日推演、输出图谱/回放/报告/验证，并能通过 workbench 按交易日查看传播链的单事件金融沙盘系统。**

如果按能力成熟度拆开看，当前已经完成了这四层：

- `1.6`：事件输入、结构化、参与者准备、belief/scenario、轻量 simulation、report/validation 的主链骨架
- `1.7`：动态事件沙盘、round-based 演化、influence graph、market state、页面化事件总览
- `1.8`：clone/population、交易化动作、trade ledger、影响驱动决策、scoreboards/counterfactual/calibration、formal flow 收口
- `1.9`：graph-first workbench、按交易日 daily replay、增量继续推演、极简首页、详细页拆分、图谱交互治理

当前系统已经不是“只有需求和 demo”的状态，而是具备：

- 可运行的 API 主链
- 可打开的产品页面
- 可验证的 Swagger 和 runtime dashboard
- 可追踪的影响链、交易链和逐日传播链
- 已合并并推送到远端 `main` 的最新 workbench 交付

## 3. 本文依据

### 3.1 已读取的历史报告

本次总结直接参考以下文档：

- [D:\lyh\agent\agent-frame\versefina\docs\reports\20260327_roadmap_1_7_与_1_6对照总结.md](D:\lyh\agent\agent-frame\versefina\docs\reports\20260327_roadmap_1_7_与_1_6对照总结.md)
- [D:\lyh\agent\agent-frame\versefina\docs\reports\20260328_roadmap_1_8_完成总结.md](D:\lyh\agent\agent-frame\versefina\docs\reports\20260328_roadmap_1_8_完成总结.md)
- [D:\lyh\agent\agent-frame\versefina\docs\reports\roadmap_1_6_execution_report.md](D:\lyh\agent\agent-frame\versefina\docs\reports\roadmap_1_6_execution_report.md)

### 3.2 本次额外参考的当前代码结构

本次还补扫了当前代码，以确认历史报告之后的真实落地情况，重点包括：

- 后端域：
  - `apps/api/src/domain/event_ingestion`
  - `apps/api/src/domain/event_structuring`
  - `apps/api/src/domain/participant_preparation`
  - `apps/api/src/domain/belief_graph`
  - `apps/api/src/domain/scenario_engine`
  - `apps/api/src/domain/event_simulation`
  - `apps/api/src/domain/influence_graph`
  - `apps/api/src/domain/simulation_ledger`
  - `apps/api/src/domain/outcome_review`
  - `apps/api/src/domain/finahunt_ingestion`
  - `apps/api/src/domain/workbench`
- 前端产品面：
  - `apps/web/src/app/event-sandbox`
  - `apps/web/src/app/workbench`
  - `apps/web/src/features/event-sandbox`
  - `apps/web/src/features/workbench`

说明：

- `roadmap_1_6_execution_report.md` 反映的是更早阶段的执行快照，其中部分“未完成”判断已被后续 `1.7`、`1.8`、`1.9` 代码和报告覆盖，因此本次只把它作为历史基线，不把它视为当前最终状态。
- `docs/reports/roadmap_1_8_execution_report.md` 当前基本为空，不作为主要依据。

## 4. 项目定位

`Versefina` 的本质不是行情终端，也不是自动交易系统，而是一个“单事件金融世界沙盘”：

- 输入一条金融事件或一个真实事件来源
- 对事件做结构化理解
- 激活参与者、clone、资金与影响关系
- 推演谁先被触发、谁跟随、谁观望、谁退出
- 让 belief、scenario、market state 随过程变化
- 通过页面和报告展示整条传播链
- 在事后做 validation、scoreboard、why/review、counterfactual

所以它的核心价值不在“秒级撮合”，而在：

- 事件如何发酵
- 谁在驱动传播
- 哪些链路导致买卖
- 哪些判断最后对了或错了

## 5. 当前总体架构

## 5.1 后端架构

后端位于 [apps/api/src](/D:/lyh/agent/agent-frame/versefina/apps/api/src)，已经形成按领域拆分的结构：

- `event_ingestion` / `event_structuring`
  - 负责事件创建、事件结构化、casebook/theme mapping 基座
- `participant_preparation` / `agent_registry`
  - 负责参与者、clone、族群、资金与准备态
- `belief_graph` / `scenario_engine`
  - 负责观点网络、情景生成与 dominant scenario
- `event_simulation` / `simulation_ledger`
  - 负责动作执行、持仓现金变化、trade ledger、round/day 结果
- `influence_graph`
  - 负责影响边和影响驱动逻辑
- `outcome_review` / `reporting`
  - 负责 replay、report、validation、why/review 相关聚合
- `finahunt_ingestion`
  - 负责从 `finahunt` runtime 产物导入真实事件
- `workbench`
  - 负责 graph-stage、trade-pulse、decision-trace、daily replay、continue-day 等工作台能力

整体上，后端已经不是一个单文件 demo API，而是面向“事件 -> 推演 -> 回放 -> 解释”的完整领域服务层。

## 5.2 前端架构

前端位于 [apps/web/src](/D:/lyh/agent/agent-frame/versefina/apps/web/src)，当前主要产品面包括：

- `event-sandbox`
  - 动态事件沙盘主产品页
- `workbench`
  - 图谱优先的工作台与按天推演页面
- `roadmap-1-6-demo`
  - 早期能力演示面，更多是历史基座与验证入口
- `admin-console` / `agent-observation` / `rankings` / `universe-panorama`
  - 为更广的产品版图预留的页面能力

其中当前最成熟、最直接代表项目状态的，是：

- `event-sandbox`
- `workbench`

## 5.3 治理与审计面

除了产品页和 API，`Versefina` 还依赖 `agentsystem` 提供标准流程治理面：

- runtime dashboard：`http://127.0.0.1:8010/versefina/runtime`
- continuity：
  - [NOW.md](D:\lyh\agent\agent-frame\versefina\NOW.md)
  - [STATE.md](D:\lyh\agent\agent-frame\versefina\STATE.md)
  - [DECISIONS.md](D:\lyh\agent\agent-frame\versefina\DECISIONS.md)
- handoff：
  - [docs/handoff/current_handoff.md](D:\lyh\agent\agent-frame\versefina\docs\handoff\current_handoff.md)

这意味着 `Versefina` 的交付并不只靠代码，还包括：

- Story 边界
- acceptance 记录
- continuity 同步
- runtime 审计

## 6. 里程碑演进：从 1.6 到 1.9

## 6.1 `roadmap_1_6`：主链骨架

`1.6` 建立的是最核心的事件主链：

- 事件输入
- 事件结构化
- 参与者准备
- belief graph
- 三情景生成
- 轻量 simulation
- replay / report / validation / why

这条线解决的是“系统有没有一条从事件到复盘的完整骨架”。

按今天的视角看，`1.6` 的价值主要是：

- 定义了 Versefina 的产品形态
- 建立了 API 和 demo 的基础契约
- 为后续事件沙盘升级留出了稳定底座

## 6.2 `roadmap_1_7`：动态事件沙盘

根据 [20260327_roadmap_1_7_与_1_6对照总结.md](D:\lyh\agent\agent-frame\versefina\docs\reports\20260327_roadmap_1_7_与_1_6对照总结.md)，`1.7` 已把 `1.6` 的骨架推进成“动态事件沙盘”：

- 轮次化事件演化
- influence graph
- market state
- replay 页面化
- event-sandbox 产品主入口
- Swagger 与 dashboard 验证链
- `finahunt -> versefina` 真实事件导入与 lineage

这一阶段，Versefina 从“会算”变成了“会展示一条动态演化过程”。

## 6.3 `roadmap_1_8`：clone、交易动作与正式收口

根据 [20260328_roadmap_1_8_完成总结.md](D:\lyh\agent\agent-frame\versefina\docs\reports\20260328_roadmap_1_8_完成总结.md)，`1.8` 完成了从参与者级到 clone/交易级的升级：

- population template 与 generator
- clone roster、capital、execution clock
- 交易化动作：`INIT_BUY / ADD_BUY / REDUCE / EXIT`
- trade ledger
- influence 对交易概率的真实驱动
- market state v2
- 单事件演化墙
- validation、scoreboards、failure taxonomy
- cross-event、counterfactual、calibration、why engine
- formal flow / continuity / acceptance 的 authoritative closeout

这一阶段，Versefina 从“能讲一条事件故事”推进到“能讲谁在以什么资金和动作参与、并能做更严肃复盘”的层级。

## 6.4 `roadmap_1_9`：workbench 与按天推演

本轮最新完成的是 `1.9` workbench 相关主链，重点变化是：

- 新增 graph-first workbench 产品面
- 把主叙事从“事件骨架 + 杂项信息堆叠”改成“当天谁买、谁卖、谁影响了谁”
- simulation/replay 从单日执行窗口叙事，进一步明确为“按交易日 daily rounds”
- 默认先生成 5 个交易日
- 支持 `继续推演下一交易日`
- workbench 首页极简化，只保留：
  - 事件催化
  - 顶部轮次切换
  - 当天图谱
- 深度信息下沉到详情页
- 图谱节点默认收起，悬停才展开
- 普通滚轮恢复页面滚动，`Ctrl/Cmd + 滚轮` 才缩放图谱

这一阶段，Versefina 从“事件页 + replay 页面”进一步推进成“适合逐日观察传播链的工作台”。

## 7. 当前已经具备的核心能力

## 7.1 事件入口与结构化

系统已经支持：

- 创建事件
- 对事件做结构化
- 按主题/类型做基础映射
- 导入真实来源事件

这让 Versefina 的输入不再只是手工 demo 文本，而是具备接入真实 runtime artifact 的能力。

## 7.2 参与者、人口与 clone 体系

系统已经支持：

- participant roster
- family / clone 结构
- 资金与 risk budget 基础状态
- 行为倾向与 execution window 偏好

这意味着沙盘中的主体不再只是抽象节点，而是具备“谁、以多大体量、在什么节奏参与”的基本语义。

## 7.3 belief / scenario / market state

系统已经支持：

- belief graph
- bull/base/bear 或等价情景输出
- dominant scenario
- 市场状态迁移

也就是说，事件推演不是单纯罗列行为，而是能把行为与观点状态、市场状态连接起来。

## 7.4 交易化 simulation 与 ledger

系统已经支持：

- round/day 级 simulation
- 交易化动作
- 股数、金额、持仓、现金前后变化
- trade ledger 与 action trace

尤其是最新的 workbench 改造之后，`daily replay` 的表达更贴近用户真实想看的结果：

- 第一天谁先买
- 第二天谁继续买、谁转卖
- 第三天谁受风险和持仓影响退出
- 某些影响链如何跨日扩散

## 7.5 influence graph 与传播链

系统已经支持：

- 影响边
- 影响强度
- 驱动后续动作的关系表达
- 在 workbench 中把“影响边”和“交易边”并列呈现

这条线是 Versefina 与普通“事件详情页”最大的差异之一，因为它强调的是“传播链”而不是“静态结论”。

## 7.6 replay / report / validation / why

系统已经支持：

- replay
- report
- validation
- reliability / scoreboards 的基础能力
- why / review / outcome 解释链
- 部分更深层的 counterfactual / calibration 能力

这意味着系统不仅能展示过程，还能开始对过程结果做事后判断与解释。

## 7.7 finahunt 接入与 lineage

根据 `1.7` 对照总结和当前代码，系统已经支持：

- 从 `finahunt` 导入事件
- 保留 lineage
- 在页面展示事件来源上下文

这一步很关键，因为它把 Versefina 从“手工输入沙盘”推进成“可承接上游金融认知系统产物的下游推演层”。

## 8. 当前产品页面与用户可见结果

## 8.1 event-sandbox

`event-sandbox` 仍然是当前项目最完整的事件总览产品面：

- 事件卡与来源
- 参与者/clone
- replay / validation
- participant drilldown
- market state / scenario / influence 等结构

它代表的是 Versefina 的“单事件沙盘总览”。

## 8.2 workbench

`workbench` 是当前最新、也最贴近“演化墙 / 交易日切换”心智的工作台：

- 首页只展示事件催化、顶部轮次和当天图谱
- 轮次按交易日切换
- 支持继续推演下一交易日
- 节点默认收起，减少信息爆炸
- 有独立 detail 页面承接深度信息

它代表的是 Versefina 的“图谱优先、按天看传播链”的产品表达。

## 8.3 Swagger 与 runtime dashboard

当前仍可通过以下入口做验证：

- Swagger：`http://127.0.0.1:8001/docs`
- Runtime dashboard：`http://127.0.0.1:8010/versefina/runtime`

这两者分别承接：

- API 合约验证
- 标准流程与治理验证

## 9. 本轮 workbench 收口的新增结果

这次 `1.9` workbench 改造，已经把此前“信息过多、单页过满、时间线在底部不易操作”的问题做了明显收束。

### 9.1 首页极简化

当前首页已改成只保留：

- 事件催化
- 顶部吸顶轮次
- 当天图谱
- 一个进入详情页的入口

这使首页更接近“5 秒看懂当天传播关系”的目标。

### 9.2 按交易日切换

当前首页和 workbench 数据都已经对齐到 daily rounds：

- `第1天 / 第2天 / 第3天`
- 默认 5 天
- 继续推演下一交易日
- 支持自动播放每日演化

### 9.3 图谱交互优化

已经完成：

- 节点拖动
- 画布缩放
- 边标签显隐
- 正常滚轮滚动页面
- `Ctrl/Cmd + 滚轮` 缩放图谱
- 所有 Agent 默认只显示小点位，hover 才展开完整卡片

### 9.4 detail 页面拆分

当前详情信息已从首页移走，统一承接到：

- `/workbench/[eventId]/detail`

这避免了首页再次变成“大而全的信息墙”。

## 10. 验证结果

本轮已确认通过的验证包括：

- 后端：
  - `python -m pytest apps/api/tests -q`
  - 结果：`82 passed`
- 前端：
  - `npm run type-check`
  - `npm run test:unit -- --run`
  - 结果：通过

人工联调已覆盖：

- Swagger：`http://127.0.0.1:8001/docs`
- workbench 页面
- workbench detail 页面
- runtime dashboard：`http://127.0.0.1:8010/versefina/runtime`

workbench 页面已经手工确认过这些点：

- 默认先看到 5 个交易日
- 顶部时间线可见并可切换
- 点击继续推演后会追加新交易日
- 首页不再堆满右侧详情和底部全量流水
- 页面滚动恢复正常
- 图谱节点默认折叠，悬停再展开

## 11. Git 与交付状态

与本次 workbench 主交付相关的代码已经：

- 提交到分支：`codex/workbench-daily-replay`
- 形成提交：`e3052db`
- 合并到本地 `main`
- 推送到远端 `origin/main`

这意味着：

- workbench 日级推演与极简首页相关代码，已经进入远端 `main`
- 代码主线已经收口

需要注意的是，仓库里仍然存在一批未整理的流程文档、运行产物和任务资产改动，这些属于治理与文档整理问题，不影响本次代码能力已经进入 `main` 的事实。

## 12. 当前仍未完全收口的事项

虽然项目已经具备可运行、可展示、可验证的完整主链，但如果以“产品终局”和“治理终局”的标准看，仍有几类问题没有完全结束。

## 12.1 文档与流程资产仍偏脏

当前工作树中仍存在：

- continuity 文件更新
- handoff 文档更新
- requirements/story 交付文件
- runtime 产物和中间文档

这说明代码主链已收口，但发布级文档卫生还可以继续整理。

## 12.2 产品终局感还有提升空间

虽然 `event-sandbox` 和 `workbench` 都已经可用，但如果目标是更强的“金融事件演化墙”终局体验，还可以继续增强：

- 图谱的成品感
- 状态迁移的可视化冲击力
- scoreboards / failure taxonomy 的产品化表达
- why / evidence trace 的直接可读性

## 12.3 更强的长期研究闭环仍可继续补强

例如：

- 更系统的代表性真实事件包
- 更明确的 `T+1 / T+3 / T+N` 回填策略
- 更稳定的 reliability / calibration 长周期看板

这些已经有基础，但还可以继续从“存在能力”提升到“日常使用的产品机制”。

## 13. 推荐的下一步

如果继续推进 `Versefina`，建议按以下顺序做：

1. 整理 `docs/`、`tasks/`、continuity/handoff 相关脏文件，让治理面和代码面重新一致
2. 统一补一轮最新的 `roadmap_1_9` authoritative 文档与正式总结，避免项目状态只留在代码里
3. 继续打磨 `workbench` 与 `event-sandbox` 的视觉成品感，让图谱、状态、验证三条线更自然地串起来
4. 固化一组代表性真实事件样本，做长期验证和对比演示
5. 视产品方向决定是继续深挖单事件研究工作台，还是把多事件、多主题联动抬成下一条正式 roadmap

## 14. 最终判断

今天的 `Versefina` 可以定义为：

**一个已经完成事件输入、结构化、参与者与 clone 激活、影响链推演、交易化 simulation、逐日 workbench、报告与验证、真实事件导入，并且拥有产品页、Swagger、runtime dashboard 三层验证面的单事件金融沙盘系统。**

它已经跨过了“需求和 demo”阶段，也已经跨过了“只有基础事件页”的阶段。

当前更准确的定位是：

- 核心主链已完成
- workbench 日级演化已完成并进入 `main`
- 产品化和治理收口仍有后续整理空间

如果只用一句话概括当前完成度：

**Versefina 已经具备“看懂一条金融事件如何在多主体之间逐步传播、交易、反转并被事后验证”的完整主链能力，下一阶段要解决的已经不再是“有没有”，而是“多成熟、多整洁、多像最终产品”。**

# Versefina Backlog v1.2 增量规划

## 规划目标

当前 `versefina` 已有两条需求线索：

1. `需求分析_1.1.md`：交割单驱动的行为镜像 Agent
2. `需求分析_1.2.md`：金融反身性引擎 / 事件推演系统

本次规划的目标不是重写已完成的 `Sprint 1`，也不是打断当前本地正在推进的 `Sprint 2` 市场世界改动，而是在保留既有 `Sprint 3 / Sprint 4` 的前提下，把 `1.2` 转化成一条新的 Versefina 高优先级交付主线。

优先级策略如下：

1. 先收口并验证当前 `Sprint 2` 的世界、撮合、账本、日循环改动。
2. `Sprint 2` 之后，优先执行 `1.2` 对应的 `Sprint 5` 到 `Sprint 8`。
3. `Sprint 3 / Sprint 4` 保留，但从“默认下一步”下调为“延后执行”的行为镜像支线。
4. `1.2` 首发只做一个事件类型，优先选择“政策催化”，避免验证口径和样本口径过早发散。
5. 把“样本台账、信号口径、失效条件”前置，把页面包装放在后置 Sprint。

## Sprint 总览

| Sprint | 状态 | 优先级 | 核心目标 |
| :--- | :--- | :--- | :--- |
| Sprint 1 交割单到 Agent 建模 | 已完成 | 已完成 | 跑通上传、解析、基础画像与 Agent 创建闭环 |
| Sprint 2 世界、撮合、账本、日循环 | 进行中 | 当前最高 | 跑通统一世界、撮合、账本与 Daily Loop |
| Sprint 5 事件反身性基线与样本台账 | 新增 | 高 | 冻结首发事件范围，建立事件契约、结构化输出和样本回放基座 |
| Sprint 6 Agent 社会与 Belief Graph | 新增 | 高 | 跑通 8 类 Agent 的结构化立场输出与信念图谱聚合 |
| Sprint 7 三剧本推演与后验验证闭环 | 新增 | 高 | 跑通资金状态迁移、三剧本、T+1/T+3 回填与 Agent 打分 |
| Sprint 8 事件产品化与 MVP 验收 | 新增 | 中高 | 完成事件卡、复盘页、批量验证与 MVP 验收包 |
| Sprint 3 行为镜像建模与策略壳 | 已规划 | 延后 | 把“画像”升级为“可运行、可约束”的行为镜像 Agent |
| Sprint 4 验证分级与只读运营控制 | 已规划 | 延后 | 把“可运行 Agent”升级为“可验证、可分级、可只读运营”的产品闭环 |

## 新增 Sprint 说明

- `Sprint 5` 对应 `需求分析_1.2.md` 第六章、第九章前半段、第十五章和第二十章里关于事件范围、结构化字段、验证口径统一的要求。
- `Sprint 6` 对应 `需求分析_1.2.md` 第九章 `Belief Engine / Belief Graph`、第十章 `8 个 Agent` 和第十一章图谱聚合设计。
- `Sprint 7` 对应 `需求分析_1.2.md` 第十二章、第十三章、第十四章和第十五章后半段的剧本、状态迁移、Outcome Tracker、Agent Scores。
- `Sprint 8` 对应 `需求分析_1.2.md` 第十七章页面设计、第十八章里程碑收口和第十九章验收标准。
- `Sprint 3 / Sprint 4` 不删除，因为 `1.1` 行为镜像路线仍然可复用现有世界和账本底座，但它已经不是当前验证 `1.2` 产品假设的最短路径。

## 建议执行顺序

1. 完成并有意识地提交或整理 `Sprint 2` 本地改动。
2. 执行 `Sprint 5`，先统一事件契约、事件样本和结构化字段。
3. 执行 `Sprint 6`，把 8 类 Agent 和 Belief Graph 跑通。
4. 执行 `Sprint 7`，把三剧本和 T+1/T+3 验证闭环接上。
5. 执行 `Sprint 8`，最后再做用户侧页面、复盘视图和验收包。
6. 如需继续行为镜像路线，再恢复 `Sprint 3` 与 `Sprint 4`。

## 目录结构

```text
docs/
  contracts/
    backlog_v1/
      sprint_overview.md
      sprint_3_behavior_mirror_modeling/
      sprint_4_validation_and_readonly_ops/
      sprint_5_event_reflexivity_foundation/
      sprint_6_agent_society_and_belief_graph/
      sprint_7_scenario_validation_loop/
      sprint_8_event_console_and_acceptance/
```

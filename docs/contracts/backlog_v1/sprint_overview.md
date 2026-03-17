# Versefina Backlog v1.1 增量规划

## 规划目标

`需求分析_1.1.md` 相比 `需求分析.md`，新增的重点不再只是“上传交割单后生成 Agent”，而是补齐了以下闭环：

1. 交易行为特征提取
2. `TradingBehaviorProfile` 结构化生成
3. 策略模板匹配与 `BehaviorMirrorPolicy` 生成
4. 行为镜像 Agent 装配
5. 留出集验证、多维评分与 Agent 分级
6. 验证报告、结构化行为解释、只读运营控制

本次规划只补充这些新增能力，不回写或重排已完成的 `Sprint 1`，也不打断当前本地正在推进的 `Sprint 2` 市场世界相关改动。

## Sprint 总览

| Sprint | 状态 | 核心目标 |
| :--- | :--- | :--- |
| Sprint 1 交割单到 Agent 建模 | 已完成 | 跑通上传、解析、基础画像与 Agent 创建闭环 |
| Sprint 2 世界、撮合、账本、日循环 | 进行中 | 跑通统一世界、撮合、账本与 Daily Loop |
| Sprint 3 行为镜像建模与策略壳 | 新增 | 把“画像”升级为“可运行、可约束”的行为镜像 Agent |
| Sprint 4 验证分级与只读运营控制 | 新增 | 把“可运行 Agent”升级为“可验证、可分级、可只读运营”的产品闭环 |

## 新增 Sprint 说明

- `Sprint 3` 对应 `需求分析_1.1.md` 第五章、第六章和第七章前半段新增内容。
- `Sprint 4` 对应 `需求分析_1.1.md` 第七章后半段、第十五章和第十八章新增内容。
- `OpenClaw Adapter` 本次不新增 Story，因为 `1.1` 明确把它降级为 stretch target / `v1.5`，不再是 MVP 阻塞项。

## 目录结构

```text
docs/
  contracts/
    backlog_v1/
      sprint_overview.md
      sprint_3_behavior_mirror_modeling/
      sprint_4_validation_and_readonly_ops/
```

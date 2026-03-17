# Sprint 3 规划

## Sprint 名称

行为镜像建模与策略壳

## Sprint 目标

把现有“交割单 -> 基础画像 -> Agent 创建”的链路升级为“交割单 -> 行为特征 -> 画像 -> 模板匹配 -> 策略壳 -> 行为镜像 Agent”的受限生成链路，降低乱交易风险，并为后续验证分级打基础。

## 做什么

- [ ] 补齐交易行为特征提取
- [ ] 落地 `TradingBehaviorProfile`
- [ ] 建立第一版策略模板库
- [ ] 完成模板匹配与 `BehaviorMirrorPolicy` 生成
- [ ] 完成行为镜像 Agent 装配

## 不做什么

- [ ] 不在本 Sprint 内完成多维评分与公开分级
- [ ] 不在本 Sprint 内完成验证报告页面
- [ ] 不把 OpenClaw 接入重新拉回 MVP 阻塞路径

## Epic 总览

| Epic | Story 数 | 核心职责 |
| :--- | :--- | :--- |
| Epic 3.1 Feature & Profile | 2 | 从 TradeRecord 提取稳定行为特征，并生成结构化画像 |
| Epic 3.2 Template & Policy | 4 | 把画像映射为模板、策略壳与行为镜像 Agent |

## 推荐执行顺序

1. S3-001
2. S3-002
3. S3-003
4. S3-004
5. S3-005
6. S3-006

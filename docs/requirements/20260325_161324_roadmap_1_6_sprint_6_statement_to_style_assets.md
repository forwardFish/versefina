# roadmap_1_6_sprint_6_statement_to_style_assets

## Context
- Project: versefina
- Delivery mode: auto
- CEO review mode: hold_scope
- Source requirement file: inline input

## User Problem
# Sprint 6 规划

## Target Audience
The primary product operators and analysts who depend on this sprint outcome.

## Requirement Summary
# Sprint 6 规划

## Sprint 名称

交割单到风格资产

## Sprint 目标

将原本第一主线的交割单链路调整为第二阶段风格资产生产线，完成上传 / 解析定位切换、行为特征提取、`MarketStyleEmbedding`、`Archetype Seed` 和参与者激活校准规则。

## 做什么

- [ ] 明确交割单为次入口
- [ ] 完成行为特征提取
- [ ] 生成 `MarketStyleEmbedding`
- [ ] 抽象 `Archetype Seed`
- [ ] 建立参与者激活校准规则

## 不做什么

- [ ] 不把交割单重新拉回第一阶段主入口
- [ ] 不直接实现完整分布校准闭环
- [ ] 不替代事件沙盘主流程

## Epic 总览

| Epic | Story 数 | 核心职责 |
| :--- | :--- | :--- |
| Epic 6.1 Statement-to-Style | 3 | 调整交割单定位并生成风格向量 |
| Epic 6.2 Archetype Calibration | 2 | 抽象母体并建立激活校准规则 |

## 推荐执行顺序

1. E6-001
2. E6-002
3. E6-003
4. E6-004
5. E6-005

Sprint roadmap_1_6_sprint_6_statement_to_style_assets should deliver the following story goals in one coordinated cycle:
- 明确交割单链路在 1.6 中的定位从主入口调整为风格资产次入口。
- 从交割单提取持仓周期、加减仓、追涨偏好和回撤容忍等行为特征。
- 把交易行为特征向量化为可用于参与者校准的 MarketStyleEmbedding。
- 从 MarketStyleEmbedding 抽象出 Archetype Seed。
- 建立事件类型与参与者风格激活关系的初始校准规则。

## Product Constraints
- Follow the formal story execution matrix.
- Do not skip review, QA, or sprint close evidence.

## Success Signals
- Every story in the sprint completes with formal evidence.
- Sprint-level framing, closeout, and acceptance artifacts are recorded.

## CEO Mode Decision
- Selected mode: hold_scope
- No scope expansion was auto-accepted.

## System Audit Snapshot
- No major UI scope detected from this requirement.
- Office-hours framing is available and should be treated as upstream context.
- Constraint count: 2 | Success signals: 2.

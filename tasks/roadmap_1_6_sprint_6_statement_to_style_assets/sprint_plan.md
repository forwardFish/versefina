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

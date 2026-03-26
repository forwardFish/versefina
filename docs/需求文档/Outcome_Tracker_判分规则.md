# Outcome Tracker 判分规则

## 回填字段

- `sector_performance`
- `leader_performance`
- `expansion_status`
- `sentiment_status`

## 实际剧本判定

- 四个字段中，正向信号占优时判定为 `bull`
- 负向信号占优时判定为 `bear`
- 正负信号混杂时判定为 `mixed`
- 仅出现局部确认或局部失效时判定为 `base`
- 证据不足时判定为 `unclear`

## 分数标签

- `hit`: 预测剧本与实际剧本一致
- `partial_hit`: 实际结果混合，只有部分验证
- `invalidated`: T+3 仍未兑现，或关键验证条件失败
- `delayed_realization`: T+1 只到达基准态，仍需等待后续兑现
- `wrong_direction`: 实际结果与预测方向相反

## 失败原因

- 行业板块未跟随
- 龙头个股未确认
- 扩散广度不足
- 情绪承接失败
- 预测剧本与实际剧本偏离

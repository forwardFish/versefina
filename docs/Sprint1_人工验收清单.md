# Sprint 1 人工验收清单

适用范围：
- `S1-001` 上传接口
- `S1-002` Statement 状态机
- `S1-003` 文件类型识别
- `S1-004` 上传失败处理
- `S1-005` 字段映射规则
- `S1-006` TradeRecord 标准化
- `S1-007` 解析校验与错误报告
- `S1-008` Profile 提取
- `S1-009` 风格标签与风控约束生成
- `S1-010` Agent 创建 API

## 1. 验收前准备

启动服务：

```powershell
cd D:\lyh\agent\agent-frame\versefina
python -m uvicorn apps.api.src.main:app --host 127.0.0.1 --port 8001
```

打开 Swagger：

- `http://127.0.0.1:8001/docs`

准备真实交割单：

- 推荐放在本地 `test/data/`
- 不要提交到 Git

## 2. 人工验收原则

每一步都要看两件事：

1. 接口返回值是否合理
2. 业务含义是否正确

如果只是返回 `200`，但内容明显不合理，也算不通过。

## 3. 推荐验收顺序

### Step 1：上传交割单

接口：

- `POST /api/v1/statements/upload`

Swagger 填写建议：

- `owner_id`: 你的测试用户，例如 `human_uat`
- `market`: `CN_A`
- `statement_id`: 建议手工填写，例如 `stmt_20260316_001`
- `file`: 选择真实交割单

通过标准：

- 返回 `200`
- `upload_status = uploaded`
- 返回 `statement_id`
- 返回 `object_key`
- `file_name` 和真实文件一致
- `byte_size` 大于 0

人工检查点：

- `statement_id` 不要再用 Swagger 默认值 `string`
- `object_key` 路径应包含 `owner_id/statement_id/原文件名`

### Step 2：查询 Statement 元数据

接口：

- `GET /api/v1/statements/{statement_id}`

通过标准：

- 返回 `200`
- `upload_status = uploaded`
- `detected_file_type` 合理
- `parser_key` 合理
- `error_code` 和 `error_message` 为空

人工检查点：

- `content_type` 与实际文件大体一致
- `detected_file_type` 与文件类型一致

### Step 3：触发解析

接口：

- `POST /api/v1/statements/{statement_id}/parse`

通过标准：

- 返回 `200`
- `final_status = parsed`
- `parsed_records > 0`
- `failed_records = 0`
- 返回 `parse_report_path`
- 返回 `trade_record_path`

人工检查点：

- 记录数是否符合预期
- 如果失败，错误信息是否可理解

注意：

- 同一个 `statement_id` 已经解析成功后，再点一次 `parse` 会因为状态机限制返回错误，这是正常行为，不代表解析能力有问题。

### Step 4：查看解析报告

接口：

- `GET /api/v1/statements/{statement_id}/parse-report`

通过标准：

- 返回 `200`
- `parsed_records` 和上一步一致
- `failed_records` 合理
- 有 `trade_record_path`

人工检查点：

- 报告中的 `broker`
- `detected_file_type`
- `parser_key`
- 是否有 issue

### Step 5：人工抽查 TradeRecord 质量

检查文件：

- `trade_record_path` 指向的 JSON 文件

人工检查点：

- `symbol` 是否正确补全 `.SH/.SZ`
- `side` 是否正确映射为 `buy/sell`
- `qty` 是否正确
- `price` 是否正确
- `fee`、`tax` 是否正确
- `traded_at` 是否是可读日期

建议至少随机抽查 5 条记录。

### Step 6：生成 Profile

接口：

- `POST /api/v1/statements/{statement_id}/profile`

通过标准：

- 返回 `200`
- `trade_record_count > 0`
- 返回 `profile_path`
- `profile.styleTags` 非空
- `profile.riskControls` 非空
- `profile.cadence` 非空

人工检查点：

- 风格标签是否符合真实交易习惯
- 偏好标的是否有代表性
- 风控参数是否在合理范围

### Step 7：创建 Agent

接口：

- `POST /api/v1/agents`

Swagger body 示例：

```json
{
  "owner_id": "human_uat",
  "statement_id": "stmt_20260316_001",
  "init_cash": 500000,
  "world_id": "cn-a",
  "source_runtime": "native"
}
```

通过标准：

- 返回 `200`
- 返回 `agent_id`
- `status = active`
- `public_url` 可用
- `profile_path` 存在

人工检查点：

- `public_url` 端口应与当前服务一致，例如 `8001`
- `statement_id`、`owner_id` 应与前面输入一致

### Step 8：查询 Agent

接口：

- `GET /api/v1/agents/{agent_id}`

通过标准：

- 返回 `200`
- `cash = init_cash`
- `equity = init_cash`
- `status = active`
- `tags` 与 profile 结果一致

人工检查点：

- `risk_controls` 与 profile 一致
- `positions` 初始应为空

### Step 9：查询 Agent Snapshot

接口：

- `GET /api/v1/agents/{agent_id}/snapshot`

通过标准：

- 返回 `200`
- `cash`、`equity`、`drawdown` 正常
- `statement_id` 正确
- `public_url` 正确

人工检查点：

- Snapshot 内容应与 Agent 主记录一致

## 4. 必测异常场景

建议至少再做 3 个异常场景：

1. 上传不支持的文件类型
- 预期：返回 `400`

2. 上传空文件
- 预期：返回 `400`

3. 上传后不先 parse，直接 profile
- 预期：返回 `409`

## 5. 人工验收结论模板

可以按下面格式记录：

```text
验收人：
验收时间：
样本文件：
statement_id：
agent_id：

结论：
- 上传：通过/不通过
- 解析：通过/不通过
- Profile：通过/不通过
- Agent 创建：通过/不通过
- Agent 查询：通过/不通过
- Snapshot：通过/不通过

备注：
```

## 6. 本轮参考结果

已验证通过的一条真实样本链路：

- 样本文件：`test/data/林燕辉_交割单.xls`
- `statement_id`: `stmt_human_144707`
- `agent_id`: `agt_stmt_human_144707`

结果摘要：

- 上传成功
- 解析成功，`parsed_records = 60`
- Profile 生成成功
- Agent 创建成功
- Agent 查询成功
- Snapshot 查询成功

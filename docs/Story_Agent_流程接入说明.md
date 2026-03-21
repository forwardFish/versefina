# Versefina Story Agent 流程接入说明

最后更新：2026-03-20

## 1. 唯一标准来源

`versefina` 不再维护第二套 Story / Sprint Agent 正式流程标准。

唯一正式标准以 `agentsystem` 为准：

- `D:/lyh/agent/agent-frame/agentsystem/docs/standards/gstack_platform_migration_spec.md`
- `D:/lyh/agent/agent-frame/agentsystem/docs/standards/story_sprint_agent_workflow_standard.md`

本文件只负责说明 `versefina` 的接入方式与 repo-specific 例外。

## 2. 默认接入规则

`versefina` 后续 Story 默认按 `agentsystem` 强制矩阵执行：

- 新需求 / 新 Epic / 新 Sprint：
  - `office-hours -> plan-ceo-review -> plan-eng-review`
- 普通 API / runtime Story：
  - `Requirement -> plan-eng-review -> Builder -> Code Style Reviewer -> Reviewer -> qa 或 qa-only -> Code Acceptance -> Acceptance Gate -> Doc Writer`
- 前端 / 页面 Story：
  - `Requirement -> browse -> design-consultation -> plan-design-review -> Builder -> Reviewer -> browse(local evidence via qa chain) -> design-review -> qa -> Acceptance -> Doc Writer`
- Bug / 回归修复：
  - `investigate -> Builder/Fixer -> Reviewer -> qa -> Acceptance -> Doc Writer`
- Sprint 收尾：
  - `ship -> document-release -> retro`

## 3. Versefina Repo-Specific 例外

- `versefina` 当前以 FastAPI API 与业务闭环验证为主，默认多数 Story 归类为后端 / runtime Story。
- 当 Story 影响 Swagger 验证链、上传解析链、agent create 流程时，`qa` 必须覆盖真实接口或手工验收路径。
- 当 Story 明确涉及页面、浏览器交互或登录态时，才强制进入前端专项链，并在需要时先跑 `setup-browser-cookies`。
- `.agents/` 下的 contract / style / review 配置仍是 repo contract，流程接入不得随意重写。

## 4. 任务字段映射建议

在 `versefina` 接入 `agentsystem` 时，任务载荷至少补齐这些字段：

- `story_kind`
- `risk_level`
- `has_browser_surface`
- `auth_expectations`
- `bug_scope`
- `investigation_context`
- `release_scope`
- `doc_targets`
- `workflow_enforcement_policy`

推荐默认值：

- API / parse / profile / create 链路 Story：
  - `story_kind=backend`
  - `has_browser_surface=false`
- 登录态或页面验收 Story：
  - `story_kind=ui`
  - `has_browser_surface=true`
- Sprint close：
  - `doc_targets=["README.md", "docs", ".agents"]`

## 5. 完成记账口径

`versefina` 后续必须把“结果完成”和“流程完成”分开记账：

- `implemented`
- `verified`
- `agentized`
- `accepted`

如果只有功能完成但没有走完要求的 Agent 链，不能视为完整交付。

## 6. 迁移要求

后续如果 `versefina` 写新的流程说明：

- 只能写 repo-specific exception
- 不能再定义独立标准
- 必须显式引用 `agentsystem` 正式标准

# VerseFina - AI Agent Development Constitution

## 0. 元规则
> 先看现有的代码怎么写，你就怎么写！不要发明新风格。
> 一次只做一个动作。如果要改多个文件，拆成多个提交。

## 1. 项目架构
- **Repo A (agentsystem)**: 通用开发工厂，**禁止**在此仓库写任何 versefina 业务逻辑。
- **Repo B (versefina)**: 业务平台，所有业务代码在此。
- **技术栈**: Next.js 14 (TS) + FastAPI (Python) + LangGraph.

## 2. 代码风格 (Code Style)

### 2.1 Python (FastAPI)
- **缩进**: 4 个空格。
- **类型**: **必须**加 Type Hints (Pydantic)。
- **命名**:
  - 类名: `AgentRegistry` (大驼峰)
  - 函数/变量: `get_agent_snapshot` (蛇形)
- **行宽**: 120 字符。
- **工具**: `ruff` 做 lint，`black` 做格式化。

### 2.2 TypeScript/React (Next.js)
- **缩进**: 2 个空格。
- **组件**: **必须**使用函数组件 + Hooks。
- **命名**:
  - 组件/文件: `AgentCard.tsx` (大驼峰)
  - 变量/函数: `fetchAgentData` (小驼峰)
- **工具**: `eslint` + `prettier`。

## 3. 目录约定
- **前端页面**: `apps/web/src/app/(dashboard)/`
- **后端 API**: `apps/api/src/api/v1/`
- **后端 Schema**: `apps/api/src/schemas/`
- **禁止区域**: `infra/prod/`, `secrets/` (碰了直接 Fail)。

## 4. 标准命令链 (Standard Commands)
在提交代码前，必须依次执行：
1. `install`: 安装依赖
2. `lint`: 代码检查
3. `typecheck`: 类型检查
4. `test`: 单元测试

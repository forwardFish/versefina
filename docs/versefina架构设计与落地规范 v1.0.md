# Repo B (versefina) 架构设计与落地规范 v1.0

## 文档版本

v1.0 | 钉死边界，空架子先行

---

## 一、文档概述

### 1.1 核心目标

本文档定义 Repo B (versefina) 的**目录结构、模块边界、路由边界、API 边界、读写分离规范以及与 Repo A 的协作方式**。

### 1.2 现阶段原则

- **先搭空架子**：不写深度业务逻辑。

- **先钉死契约**：所有目录、接口、规则、配置文件先定。

- **为 Repo A 铺路**：设计成“可被 Repo A 开发”的标准目标仓。

---

## 二、Repo B 总定位

Repo B 是**Agent-native 金融世界业务平台**。

- **它不是**：Agent 框架本身。

- **它是**：被开发的目标产品。

- **核心形态**：只读观察层 + 平行宇宙展示层 + 平台入口层。

---

## 三、Repo B 前端架构设计 v1.0

### 3.1 技术栈

- **框架**：Next.js 14+ (App Router)

- **语言**：TypeScript

- **包管理**：pnpm

- **UI 组件**：Ant Design

- **图表**：ECharts

- **数据请求**：TanStack Query (React Query)

- **轻量状态**：Zustand

### 3.2 前端分层

1. **App Layer**：路由、Layout、页面入口、鉴权。

2. **Feature Layer**：onboarding, agent-observation, rankings, universe-panorama。

3. **Entity Layer**：agent, world, trade-log, ranking, snapshot。

4. **Shared UI Layer**：通用组件、图表、表格。

5. **Data Access Layer**：统一封装 Query API 调用。

### 3.3 前端目录结构

```Plain Text

versefina/
└── apps/
    └── web/
        ├── src/
        │   ├── app/
        │   │   ├── (public)/
        │   │   │   ├── page.tsx              # 首页
        │   │   │   └── share/[shareId]/
        │   │   ├── (auth)/
        │   │   │   └── login/
        │   │   └── (dashboard)/
        │   │       ├── layout.tsx
        │   │       ├── onboarding/
        │   │       ├── agents/[agentId]/
        │   │       │   ├── page.tsx          # 观测站核心
        │   │       │   ├── trades/
        │   │       │   └── equity/
        │   │       ├── rankings/
        │   │       ├── universe/
        │   │       └── admin/
        │   ├── features/
        │   │   ├── onboarding/
        │   │   ├── agent-observation/
        │   │   ├── rankings/
        │   │   ├── universe-panorama/
        │   │   ├── public-share/
        │   │   └── admin-console/
        │   ├── entities/
        │   │   ├── agent/
        │   │   ├── world/
        │   │   ├── trade-log/
        │   │   ├── ranking/
        │   │   └── snapshot/
        │   ├── shared/
        │   │   ├── ui/
        │   │   ├── charts/
        │   │   ├── table/
        │   │   ├── layout/
        │   │   ├── hooks/
        │   │   ├── lib/
        │   │   ├── constants/
        │   │   └── types/
        │   ├── services/
        │   │   ├── api/
        │   │   ├── query/
        │   │   └── mapper/
        │   ├── store/
        │   │   └── ui-store/
        │   └── styles/
        ├── middleware.ts
        ├── env.ts
        ├── package.json
        └── tsconfig.json
```

### 3.4 前端核心页面清单

|页面|路径|核心功能|数据来源|
|---|---|---|---|
|首页|`/`|产品介绍、入口跳转|-|
|接入页|`/onboarding`|上传交割单、创建 Agent|Command API|
|Agent 观测站|`/agents/[agentId]`|概览、持仓、收益、日志 (**只读**)|Read Model|
|排行榜|`/rankings`|收益/回撤/稳定性榜单|Read Model|
|宇宙全景|`/universe`|世界快照、生态动态|Read Model|
|公开分享页|`/share/[shareId]`|匿名化分享|Read Model|
---

## 四、Repo B 后端架构设计 v1.0

### 4.1 技术栈

- **语言**：Python

- **Web 框架**：FastAPI

- **ORM**：SQLAlchemy

- **迁移**：Alembic

- **数据库**：PostgreSQL

- **缓存/队列**：Redis

- **异步任务**：Celery / RQ

- **编排**：LangGraph

- **数据校验**：Pydantic

### 4.2 后端分层

1. **Gateway Layer**：路由、鉴权、限流、审计。

2. **Command Layer**：处理写请求 (异步)。

3. **Query Layer**：处理读请求 (只读 Read Model)。

4. **Domain Layer**：核心业务 (agent_registry, dna_engine, market_world, simulation_ledger)。

5. **Workflow Layer**：LangGraph 工作流。

6. **Projection Layer**：事件消费，构建读模型。

7. **Adapter Layer**：OpenClaw 等外部接入。

### 4.3 后端目录结构

```Plain Text

versefina/
└── apps/
    ├── api/
    │   ├── src/
    │   │   ├── main.py
    │   │   ├── app.py
    │   │   ├── api/
    │   │   │   ├── gateway/
    │   │   │   ├── command/
    │   │   │   ├── query/
    │   │   │   ├── admin/
    │   │   │   └── adapter/
    │   │   ├── domain/
    │   │   │   ├── agent_registry/
    │   │   │   ├── dna_engine/
    │   │   │   ├── market_world/
    │   │   │   ├── simulation_ledger/
    │   │   │   └── platform_control/
    │   │   ├── workflows/
    │   │   │   ├── statement_ingestion/
    │   │   │   ├── daily_simulation/
    │   │   │   └── review/
    │   │   ├── projection/
    │   │   │   ├── agent_snapshots/
    │   │   │   ├── rankings/
    │   │   │   └── panorama/
    │   │   ├── infra/
    │   │   │   ├── db/
    │   │   │   ├── cache/
    │   │   │   ├── bus/
    │   │   │   ├── storage/
    │   │   │   ├── scheduler/
    │   │   │   ├── auth/
    │   │   │   └── audit/
    │   │   ├── schemas/
    │   │   ├── services/
    │   │   ├── settings/
    │   │   └── tests/
    │   ├── requirements.txt
    │   └── pyproject.toml
    │
    └── worker/
        ├── src/
        │   ├── main.py
        │   ├── jobs/
        │   ├── consumers/
        │   ├── shard_runtime/
        │   └── tests/
        ├── requirements.txt
        └── pyproject.toml
```

### 4.4 后端核心领域模块边界

|模块|核心职责|绝不负责|
|---|---|---|
|**Agent Registry**|身份、状态、心跳、信任等级|交易账本、市场世界|
|**DNA Engine**|交割单解析、特征提取、标签生成|运行时交易|
|**Market World**|日历、快照、候选池、世界时钟|持仓、收益|
|**Simulation Ledger**|现金、持仓、日志、PnL、Append-only|世界状态、前端聚合|
|**Platform Control**|权限、风控、总开关、配额|页面展示|
---

## 五、API 边界设计 (核心契约)

### 5.1 Command API (写请求)

只返回 `accepted` 或 `task_id`，不直接返回最终状态。

- `POST /api/v1/statements/upload`

- `POST /api/v1/agents/register`

- `POST /api/v1/agents/{agent_id}/heartbeat`

- `POST /api/v1/actions/submit`

### 5.2 Query API (读请求)

**只读 Read Model**，绝不查原始账本。

- `GET /api/v1/agents/{agent_id}/snapshot`

- `GET /api/v1/agents/{agent_id}/trades`

- `GET /api/v1/agents/{agent_id}/equity`

- `GET /api/v1/rankings`

- `GET /api/v1/universe/panorama`

- `GET /api/v1/worlds/{world_id}/snapshot`

### 5.3 Adapter API (OpenClaw 专用)

- `POST /api/v1/adapter/openclaw/register`

- `POST /api/v1/adapter/openclaw/heartbeat`

- `GET /api/v1/adapter/openclaw/world-state`

- `POST /api/v1/adapter/openclaw/submit-action`

---

## 六、与 Repo A 的协作规范

### 6.1 Repo A 可触碰的区域

- `apps/api/src/domain/**`

- `apps/api/src/api/**`

- `apps/api/src/workflows/**`

- `apps/api/src/projection/**`

- `apps/web/src/features/**`

- `apps/web/src/entities/**`

- `tests/**`

### 6.2 Repo A 严禁触碰的区域

- `infra/prod/**`

- `secrets/**`

- `docker/**` (生产配置)

- `.github/workflows/prod-*`

### 6.3 核心 `.agents` 配置文件

Repo B 根目录必须包含：

1. `project.yaml`：项目技术栈全貌。

2. `rules.yaml`：边界规则、保护路径。

3. `commands.yaml`：安装、测试、构建命令。

4. `review_policy.yaml`：PR 审查门槛。

5. `contracts.yaml`：数据契约。

---

## 七、落地执行清单 (立即执行)

### 第一步：初始化空仓

1. [ ] 创建 GitHub 仓库 `versefina`。

2. [ ] 按本文档 `3.3` 和 `4.3` 建立**完整的空目录树**。

3. [ ] 创建 `apps/web/package.json` (Next.js)。

4. [ ] 创建 `apps/api/pyproject.toml` (FastAPI)。

### 第二步：钉死契约

1. [ ] 编写 `.agents/project.yaml`。

2. [ ] 编写 `.agents/commands.yaml`。

3. [ ] 编写 `.agents/rules.yaml`。

4. [ ] 编写后端 `schemas/` 基础 Pydantic 模型壳子。

5. [ ] 编写前端 `types/` 基础 TypeScript 定义。

### 第三步：跑通 Hello World

1. [ ] 后端：启动 FastAPI，访问 `/health` 返回 200。

2. [ ] 前端：启动 Next.js，访问 `/` 显示首页。

3. [ ] 提交第一版代码到 `main`。

---

## 八、总结

当前这一步，不是先写业务，而是先把 Repo B 设计成一个**“结构清晰、边界明确、可被 Repo A 开发”**的标准目标仓。

**空架子搭好，契约钉死，后面 Repo A 才能逐步填充血肉。**
> （注：文档部分内容可能由 AI 生成）
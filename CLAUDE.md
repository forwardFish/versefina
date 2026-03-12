# VerseFina - AI Agent Development Constitution

## 0. Meta Rules
> Follow the existing codebase style before introducing anything new.
> Make one logical change at a time. If multiple files must change, keep commits focused.

## 1. Project Architecture
- `agentsystem` is Repo A, the development factory. Do not place VerseFina business logic there.
- `versefina` is Repo B, the target business platform. All business code belongs here.
- Stack: Next.js + TypeScript, FastAPI + Python, LangGraph-based automation.

## 2. Code Style

### 2.1 Python
- Use 4 spaces for indentation.
- Add type hints for public functions and data structures.
- Prefer `snake_case` for variables/functions and `PascalCase` for classes.
- Keep lines within 120 characters when practical.
- Use `ruff` for linting and keep formatting consistent with the existing project.

### 2.2 TypeScript and React
- Use 2 spaces for indentation.
- Prefer function components and hooks.
- Use `camelCase` for variables/functions and `PascalCase` for components/files.
- Follow the established Next.js app-router structure.
- Use `eslint` and keep formatting aligned with the current codebase.

## 3. Directory Conventions
- Frontend pages: `apps/web/src/app/(dashboard)/`
- Backend API: `apps/api/src/api/`
- Backend schemas: `apps/api/src/schemas/`
- Protected areas: `infra/prod/`, `secrets/`

## 4. Standard Command Chain
Before a change is considered complete, run these in order:
1. `install`
2. `lint`
3. `typecheck`
4. `test`

## 5. Git Commit Format
Use `type(scope): description`

Examples:
- `feat(agent): add snapshot schema`
- `fix(web): resolve dashboard layout crash`

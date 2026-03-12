# Versefina

Versefina is an agent-native finance world scaffold. This repository is the target product repository in the dual-repo workflow, and is designed to be readable by Repo A through `.agents/`.

## What is included

- `apps/web`: Next.js frontend scaffold
- `apps/api`: FastAPI backend scaffold with mock read-model endpoints
- `apps/worker`: standalone worker scaffold
- `.agents`: machine-readable project contract for Repo A

## Local startup

1. Start infrastructure:

```powershell
docker compose up -d
```

2. Install dependencies:

```powershell
pnpm --dir apps/web install
pip install -r apps/api/requirements.txt
pip install -r apps/worker/requirements.txt
```

3. Start services:

```powershell
python -m apps.api.src.main
python -m apps.worker.src.main
pnpm --dir apps/web dev
```

## Mock endpoints

- `GET /health`
- `GET /api/v1/agents/mock_agent_001/snapshot`
- `GET /api/v1/universe/panorama`

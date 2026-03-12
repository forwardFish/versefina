from __future__ import annotations

import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

try:  # pragma: no cover - exercised when FastAPI is installed
    from fastapi.middleware.cors import CORSMiddleware
except ImportError:  # pragma: no cover - default in compile-only environments
    CORSMiddleware = None

from api.adapter.openclaw import build_openclaw_router  # noqa: E402
from api.admin.routes import build_admin_router  # noqa: E402
from api.command.routes import build_command_router  # noqa: E402
from api.gateway.routes import build_gateway_router  # noqa: E402
from api.query.routes import build_query_router  # noqa: E402
from infra.http import FastAPI  # noqa: E402
from services.container import build_container  # noqa: E402


def create_app() -> FastAPI:
    container = build_container()
    app = FastAPI(title="VerseFina API")
    if CORSMiddleware is not None and hasattr(app, "add_middleware"):
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    router_names = ["gateway", "command", "query", "admin", "adapter.openclaw"]
    app.include_router(build_gateway_router(router_names))
    app.include_router(build_command_router(container))
    app.include_router(build_query_router(container))
    app.include_router(build_admin_router(container))
    app.include_router(build_openclaw_router(container))
    app.state.container = container
    return app

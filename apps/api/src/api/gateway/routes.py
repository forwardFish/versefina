from __future__ import annotations

from infra.http import APIRouter
from schemas.common import HealthResponse


def build_gateway_router(router_names: list[str]) -> APIRouter:
    router = APIRouter(tags=["gateway"])

    @router.get("/health")
    def health() -> HealthResponse:
        return HealthResponse(service="versefina-api", status="ok", routers=router_names)

    return router

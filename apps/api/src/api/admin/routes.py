from __future__ import annotations

from infra.http import APIRouter
from services.container import ServiceContainer


def build_admin_router(container: ServiceContainer) -> APIRouter:
    router = APIRouter(tags=["admin"])

    @router.get("/api/v1/admin/control-plane")
    def control_plane_summary():
        return container.platform_control.policy_summary()

    return router

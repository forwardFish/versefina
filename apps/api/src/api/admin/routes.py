from __future__ import annotations

from infra.http import APIRouter
from schemas.command import TradeCalendarSyncRequest
from services.container import ServiceContainer


def build_admin_router(container: ServiceContainer) -> APIRouter:
    router = APIRouter(tags=["admin"])

    @router.get("/api/v1/admin/control-plane")
    def control_plane_summary():
        return container.platform_control.policy_summary()

    @router.post("/api/v1/admin/worlds/{world_id}/calendar/sync")
    def sync_trade_calendar(world_id: str, payload: TradeCalendarSyncRequest):
        return container.market_world.sync_calendar(world_id, payload)

    return router

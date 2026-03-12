from __future__ import annotations

from infra.http import APIRouter
from schemas.adapter import OpenClawHeartbeatRequest, OpenClawRegisterRequest, OpenClawSubmitActionRequest
from schemas.command import HeartbeatRequest, SubmitActionRequest
from services.container import ServiceContainer


def build_openclaw_router(container: ServiceContainer) -> APIRouter:
    router = APIRouter(tags=["adapter", "openclaw"])

    @router.post("/api/v1/adapter/openclaw/register")
    def register(payload: OpenClawRegisterRequest):
        return {
            "status": "accepted",
            "binding_id": f"openclaw::{payload.openclaw_agent_id}",
            "agent_id": payload.agent_id,
        }

    @router.post("/api/v1/adapter/openclaw/heartbeat")
    def heartbeat(payload: OpenClawHeartbeatRequest):
        mapped = HeartbeatRequest(heartbeat_at=payload.heartbeat_at)
        return container.agent_registry.heartbeat(payload.openclaw_agent_id, mapped)

    @router.get("/api/v1/adapter/openclaw/world-state")
    def world_state():
        return container.market_world.panorama()

    @router.post("/api/v1/adapter/openclaw/submit-action")
    def submit_action(payload: OpenClawSubmitActionRequest):
        mapped = SubmitActionRequest(
            agent_id=payload.openclaw_agent_id,
            world_id=payload.world_id,
            actions=payload.actions,
        )
        return container.simulation_ledger.submit_actions(mapped)

    return router

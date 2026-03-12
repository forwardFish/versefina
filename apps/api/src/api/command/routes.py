from __future__ import annotations

from infra.http import APIRouter
from schemas.command import AgentRegisterRequest, HeartbeatRequest, StatementUploadRequest, SubmitActionRequest
from services.container import ServiceContainer


def build_command_router(container: ServiceContainer) -> APIRouter:
    router = APIRouter(tags=["command"])

    @router.post("/api/v1/statements/upload")
    def upload_statement(payload: StatementUploadRequest):
        return container.dna_engine.ingest_statement(payload)

    @router.post("/api/v1/agents/register")
    def register_agent(payload: AgentRegisterRequest):
        return container.agent_registry.register(payload)

    @router.post("/api/v1/agents/{agent_id}/heartbeat")
    def heartbeat(agent_id: str, payload: HeartbeatRequest):
        return container.agent_registry.heartbeat(agent_id, payload)

    @router.post("/api/v1/actions/submit")
    def submit_actions(payload: SubmitActionRequest):
        return container.simulation_ledger.submit_actions(payload)

    return router

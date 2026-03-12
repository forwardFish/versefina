from __future__ import annotations

from infra.http import APIRouter
from services.container import ServiceContainer


def build_query_router(container: ServiceContainer) -> APIRouter:
    router = APIRouter(tags=["query"])

    @router.get("/api/v1/agents/{agent_id}/snapshot")
    def agent_snapshot(agent_id: str):
        return container.agent_snapshots.present(container.agent_registry.snapshot(agent_id))

    @router.get("/api/v1/agents/{agent_id}/trades")
    def agent_trades(agent_id: str):
        return container.simulation_ledger.trades(agent_id)

    @router.get("/api/v1/agents/{agent_id}/equity")
    def agent_equity(agent_id: str):
        return container.simulation_ledger.equity(agent_id)

    @router.get("/api/v1/rankings")
    def rankings():
        return container.rankings.list_rankings()

    @router.get("/api/v1/universe/panorama")
    def panorama():
        return container.panorama.present(container.market_world.panorama())

    @router.get("/api/v1/worlds/{world_id}/snapshot")
    def world_snapshot(world_id: str):
        return container.market_world.snapshot(world_id)

    return router

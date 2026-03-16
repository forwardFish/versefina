from __future__ import annotations

import json
from pathlib import Path

from infra.http import APIRouter
from services.container import ServiceContainer
from settings.base import get_settings


def build_query_router(container: ServiceContainer) -> APIRouter:
    router = APIRouter(tags=["query"])

    @router.get("/api/v1/agents/{agent_id}/snapshot")
    def agent_snapshot(agent_id: str):
        return container.agent_snapshots.present(container.agent_registry.snapshot(agent_id))

    @router.get("/api/v1/agents/{agent_id}")
    def agent_detail(agent_id: str):
        agent = container.agent_registry.get_agent(agent_id)
        if agent is None:
            return {"agent_id": agent_id, "status": "not_found"}
        return agent

    @router.get("/api/v1/agents/{agent_id}/trades")
    def agent_trades(agent_id: str):
        return container.simulation_ledger.trades(agent_id)

    @router.get("/api/v1/agents/{agent_id}/equity")
    def agent_equity(agent_id: str):
        return container.simulation_ledger.equity(agent_id)

    @router.get("/api/v1/statements/{statement_id}")
    def statement_detail(statement_id: str):
        metadata = container.statement_ingestion.get_statement(statement_id)
        if metadata is None:
            return {"statement_id": statement_id, "status": "not_found"}
        return metadata

    @router.get("/api/v1/statements/{statement_id}/parse-report")
    def statement_parse_report(statement_id: str):
        report_path = Path(get_settings().statement_parse_report_root) / f"{statement_id}.json"
        if not report_path.exists():
            return {"statement_id": statement_id, "status": "not_found"}
        return json.loads(report_path.read_text(encoding="utf-8"))

    @router.get("/api/v1/statements/{statement_id}/profile")
    def statement_profile(statement_id: str):
        profile = container.dna_engine.get_profile(statement_id)
        if profile is None:
            return {"statement_id": statement_id, "status": "not_found"}
        return profile

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

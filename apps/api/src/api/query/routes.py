from __future__ import annotations

import json
from pathlib import Path

from domain.acceptance_pack.service import AcceptancePackError
from domain.outcome_review.service import OutcomeReviewError
from domain.reporting.service import ReportingError
from domain.mirror_agent.service import MirrorAgentError
from domain.style_embedding.service import StyleEmbeddingError
from infra.http import APIRouter
from services.container import ServiceContainer
from settings.base import get_settings


def build_query_router(container: ServiceContainer) -> APIRouter:
    router = APIRouter(tags=["query"])

    @router.get("/api/v1/demo/runtime-showcase")
    def runtime_showcase():
        return container.demo_showcase.build_showcase().to_dict()

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

    @router.get("/api/v1/events/{event_id}")
    def event_detail(event_id: str):
        casebook = container.event_casebook.load_casebook(event_id)
        if casebook is not None:
            return casebook.to_dict()
        record = container.event_ingestion.load_record(event_id)
        if record is None:
            return {"event_id": event_id, "status": "not_found"}
        return record.to_dict()

    @router.get("/api/v1/events/{event_id}/casebook")
    def event_casebook(event_id: str):
        casebook = container.event_casebook.load_casebook(event_id)
        if casebook is None:
            return {"event_id": event_id, "status": "not_found"}
        return casebook.to_dict()

    @router.get("/api/v1/events/{event_id}/participants")
    def event_participants(event_id: str):
        return container.event_sandbox.load_participants(event_id)

    @router.get("/api/v1/events/{event_id}/simulation")
    def event_simulation_summary(event_id: str):
        return container.event_sandbox.load_simulation(event_id)

    @router.get("/api/v1/events/{event_id}/simulation/rounds")
    def event_simulation_rounds(event_id: str):
        return container.event_sandbox.load_rounds(event_id)

    @router.get("/api/v1/events/{event_id}/simulation/rounds/{round_key}")
    def event_simulation_round_detail(event_id: str, round_key: str):
        return container.event_sandbox.load_round(event_id, round_key)

    @router.get("/api/v1/events/{event_id}/simulation/action-log")
    def event_simulation_action_log(event_id: str):
        return container.simulation_ledger.load_action_log(event_id).to_dict()

    @router.get("/api/v1/events/{event_id}/simulation/state-snapshots")
    def event_simulation_state_snapshots(event_id: str):
        return container.simulation_ledger.load_state_snapshots(event_id).to_dict()

    @router.get("/api/v1/events/{event_id}/influence-graph")
    def event_influence_graph(event_id: str):
        return container.event_sandbox.load_influence_graph(event_id)

    @router.get("/api/v1/events/{event_id}/influence-graph/{round_key}")
    def event_influence_graph_round(event_id: str, round_key: str):
        return container.event_sandbox.load_influence_graph_round(event_id, round_key)

    @router.get("/api/v1/events/{event_id}/belief")
    def event_belief_rounds(event_id: str):
        return container.event_sandbox.load_belief(event_id)

    @router.get("/api/v1/events/{event_id}/belief/{round_key}")
    def event_belief_round(event_id: str, round_key: str):
        return container.event_sandbox.load_belief_round(event_id, round_key)

    @router.get("/api/v1/events/{event_id}/scenarios")
    def event_scenario_rounds(event_id: str):
        return container.event_sandbox.load_scenarios(event_id)

    @router.get("/api/v1/events/{event_id}/scenarios/{round_key}")
    def event_scenario_round(event_id: str, round_key: str):
        return container.event_sandbox.load_scenario_round(event_id, round_key)

    @router.get("/api/v1/events/{event_id}/replay")
    def event_replay(event_id: str):
        return container.event_sandbox.load_replay(event_id)

    @router.get("/api/v1/events/{event_id}/report")
    def event_report(event_id: str):
        return container.event_sandbox.load_report(event_id)

    @router.get("/api/v1/events/{event_id}/validation")
    def event_validation(event_id: str):
        return container.event_sandbox.load_validation(event_id)


    @router.get("/api/v1/events/{event_id}/card")
    def event_card(event_id: str):
        try:
            return container.event_cards.present(event_id).to_dict()
        except FileNotFoundError:
            return {"event_id": event_id, "status": "not_found"}

    @router.get("/api/v1/events/{event_id}/report-card")
    def report_card(event_id: str):
        try:
            return container.reporting.build_report_card(event_id).to_dict()
        except ReportingError as exc:
            return {"event_id": event_id, "status": "not_found", "error_code": exc.code, "error_message": exc.message}

    @router.get("/api/v1/events/{event_id}/review-report")
    def review_report(event_id: str):
        try:
            return container.reporting.build_review_report(event_id).to_dict()
        except ReportingError as exc:
            return {"event_id": event_id, "status": "not_found", "error_code": exc.code, "error_message": exc.message}

    @router.get("/api/v1/events/{event_id}/outcomes")
    def event_outcomes(event_id: str):
        outcomes = [item.to_dict() for item in container.outcome_review.list_outcomes(event_id)]
        latest_outcome = outcomes[-1] if outcomes else {"status": "outcome_missing"}
        return {
            "event_id": event_id,
            "status": "ready" if outcomes else "outcome_missing",
            "outcomes": outcomes,
            "latest_outcome": latest_outcome,
        }

    @router.get("/api/v1/events/{event_id}/reliability")
    def event_reliability(event_id: str):
        try:
            return container.outcome_review.build_reliability_summary(event_id).to_dict()
        except OutcomeReviewError as exc:
            return {"event_id": event_id, "status": "not_found", "error_code": exc.code, "error_message": exc.message}

    @router.get("/api/v1/events/{event_id}/why")
    def event_why(event_id: str):
        try:
            return container.reporting.build_why_report(event_id).to_dict()
        except ReportingError as exc:
            return {"event_id": event_id, "status": "not_found", "error_code": exc.code, "error_message": exc.message}

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

    @router.get("/api/v1/statements/{statement_id}/style-features")
    def statement_style_features(statement_id: str):
        features = container.style_embedding.load_behavior_features(statement_id)
        if features is None:
            return {"statement_id": statement_id, "status": "not_found"}
        return features.to_dict()

    @router.get("/api/v1/statements/{statement_id}/style-embedding")
    def statement_style_embedding(statement_id: str):
        embedding = container.style_embedding.load_market_style_embedding(statement_id)
        if embedding is None:
            return {"statement_id": statement_id, "status": "not_found"}
        return embedding.to_dict()

    @router.get("/api/v1/statements/{statement_id}/archetype-seed")
    def statement_archetype_seed(statement_id: str):
        seed = container.style_embedding.load_archetype_seed(statement_id)
        if seed is None:
            return {"statement_id": statement_id, "status": "not_found"}
        return seed.to_dict()

    @router.get("/api/v1/statements/{statement_id}/activation-calibration")
    def statement_activation_calibration(statement_id: str):
        try:
            calibration = container.style_embedding.load_activation_calibration(statement_id)
        except StyleEmbeddingError as exc:
            return {"statement_id": statement_id, "status": "not_found", "error_code": exc.code, "error_message": exc.message}
        if calibration is None:
            return {"statement_id": statement_id, "status": "not_found"}
        return calibration.to_dict()

    @router.get("/api/v1/statements/{statement_id}/mirror-agent")
    def statement_mirror_agent(statement_id: str):
        try:
            agent = container.mirror_agent.load_mirror_agent(statement_id)
        except MirrorAgentError as exc:
            return {"statement_id": statement_id, "status": "not_found", "error_code": exc.code, "error_message": exc.message}
        if agent is None:
            return {"statement_id": statement_id, "status": "not_found"}
        return agent.to_dict()

    @router.get("/api/v1/statements/{statement_id}/mirror-agent/validation")
    def statement_mirror_validation(statement_id: str):
        try:
            validation = container.mirror_agent.load_mirror_validation(statement_id)
        except MirrorAgentError as exc:
            return {"statement_id": statement_id, "status": "not_found", "error_code": exc.code, "error_message": exc.message}
        if validation is None:
            return {"statement_id": statement_id, "status": "not_found"}
        return validation.to_dict()

    @router.get("/api/v1/statements/{statement_id}/distribution-calibration")
    def statement_distribution_calibration(statement_id: str):
        summary = container.calibration.load_distribution_calibration(statement_id)
        if summary is None:
            return {"statement_id": statement_id, "status": "not_found"}
        return summary.to_dict()

    @router.get("/api/v1/statements/{statement_id}/weight-feedback")
    def statement_weight_feedback(statement_id: str):
        feedback = container.calibration.load_weight_feedback(statement_id)
        if feedback is None:
            return {"statement_id": statement_id, "status": "not_found"}
        return feedback.to_dict()

    @router.get("/api/v1/roadmaps/1.6/acceptance-pack")
    def roadmap_acceptance_pack():
        try:
            pack = container.acceptance_pack.load_acceptance_pack()
        except AcceptancePackError as exc:
            return {"roadmap_id": "roadmap_1_6", "status": "not_found", "error_code": exc.code, "error_message": exc.message}
        if pack is None:
            return {"roadmap_id": "roadmap_1_6", "status": "not_found"}
        return pack.to_dict()

    @router.get("/api/v1/rankings")
    def rankings():
        return container.rankings.list_rankings()

    @router.get("/api/v1/universe/panorama")
    def panorama(as_of_date: str | None = None):
        return container.panorama.present(container.market_world.panorama(as_of_date=as_of_date))

    @router.get("/api/v1/worlds/{world_id}/snapshot")
    def world_snapshot(world_id: str, as_of_date: str | None = None):
        return container.market_world.snapshot(world_id, as_of_date=as_of_date)

    return router

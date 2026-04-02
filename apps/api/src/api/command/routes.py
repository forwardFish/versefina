from __future__ import annotations

from dataclasses import asdict

from domain.acceptance_pack.service import AcceptancePackError
from domain.event_ingestion.service import EventIngestionError
from domain.finahunt_ingestion.service import FinahuntIngestionError
from domain.event_sandbox.service import EventSandboxError
from domain.mirror_agent.service import MirrorAgentError
from domain.outcome_review.service import OutcomeReviewError
from domain.event_simulation.service import EventSimulationError
from domain.belief_graph.service import BeliefGraphError
from domain.participant_preparation.service import ParticipantPreparationError
from domain.scenario_engine.service import ScenarioEngineError
from domain.style_embedding.service import StyleEmbeddingError
from infra.http import APIRouter, File, Form, JSONResponse, Request, UploadFile
from modules.statements.parser_service import StatementParseError
from modules.statements.service import StatementUploadValidationError
from modules.statements.status_machine import InvalidStatementTransitionError
from schemas.command import (
    AgentCreateRequest,
    AgentRegisterRequest,
    EventCreateRequest,
    FinahuntEventImportRequest,
    HeartbeatRequest,
    OutcomeReviewWriteRequest,
    StatementStatusUpdateRequest,
    StatementUploadRequest,
    SubmitActionRequest,
    WorkbenchAskRequest,
)
from services.container import ServiceContainer


def build_command_router(container: ServiceContainer) -> APIRouter:
    router = APIRouter(tags=["command"])

    @router.post("/api/v1/statements/upload")
    async def upload_statement(
        owner_id: str = Form(...),
        market: str = Form("CN_A"),
        statement_id: str | None = Form(None),
        file: UploadFile = File(...),
    ):
        file_bytes = await file.read()
        payload = StatementUploadRequest(
            statement_id=statement_id,
            owner_id=owner_id,
            file_name=file.filename or "statement.bin",
            content_type=file.content_type or "application/octet-stream",
            byte_size=len(file_bytes),
            market=market,
        )
        try:
            result = container.statement_ingestion.ingest_statement(payload, file_bytes)
        except StatementUploadValidationError as exc:
            rejected = container.statement_ingestion.reject_upload(
                owner_id=owner_id,
                file_name=payload.file_name,
                content_type=payload.content_type,
                byte_size=payload.byte_size,
                market=market,
                statement_id=statement_id,
                code=exc.code,
                message=exc.message,
            )
            return JSONResponse(status_code=exc.status_code, content=asdict(rejected))
        return asdict(result)

    @router.post("/api/v1/events")
    def create_event(payload: EventCreateRequest):
        try:
            return asdict(container.event_ingestion.ingest_event(payload))
        except EventIngestionError as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={"error_code": exc.code, "error_message": exc.message},
            )

    @router.post("/api/v1/events/from-finahunt")
    def create_event_from_finahunt(payload: FinahuntEventImportRequest):
        try:
            return asdict(container.finahunt_ingestion.import_event(payload))
        except (FinahuntIngestionError, EventIngestionError, EventSandboxError) as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={"error_code": exc.code, "error_message": exc.message},
            )

    @router.post("/api/v1/events/{event_id}/prepare")
    def prepare_event(event_id: str):
        try:
            return asdict(container.participant_preparation.prepare_event(event_id))
        except ParticipantPreparationError as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "event_id": event_id,
                    "error_code": exc.code,
                    "error_message": exc.message,
                },
            )

    @router.post("/api/v1/agents/register")
    def register_agent(payload: AgentRegisterRequest):
        return container.agent_registry.register(payload)

    @router.post("/api/v1/statements/{statement_id}/profile")
    def build_statement_profile(statement_id: str):
        metadata = container.statement_ingestion.get_statement(statement_id)
        if metadata is None:
            return JSONResponse(
                status_code=404,
                content={
                    "statement_id": statement_id,
                    "error_code": "STATEMENT_NOT_FOUND",
                    "error_message": "Statement metadata not found.",
                },
            )
        if metadata.upload_status != "parsed":
            return JSONResponse(
                status_code=409,
                content={
                    "statement_id": statement_id,
                    "error_code": "STATEMENT_NOT_PARSED",
                    "error_message": "Statement must be parsed before profile generation.",
                },
            )
        try:
            result = container.dna_engine.build_profile(statement_id, market=metadata.market)
        except FileNotFoundError:
            return JSONResponse(
                status_code=404,
                content={
                    "statement_id": statement_id,
                    "error_code": "TRADE_RECORDS_NOT_FOUND",
                    "error_message": "Trade records not found for profile generation.",
                },
            )
        return asdict(result)

    @router.post("/api/v1/statements/{statement_id}/style-features")
    def build_statement_style_features(statement_id: str):
        try:
            return container.style_embedding.extract_behavior_features(statement_id).to_dict()
        except StyleEmbeddingError as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "statement_id": statement_id,
                    "error_code": exc.code,
                    "error_message": exc.message,
                },
            )

    @router.post("/api/v1/events/{event_id}/structure")
    def structure_event(event_id: str):
        try:
            return container.event_sandbox.structure_event(event_id)
        except EventSandboxError as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "event_id": event_id,
                    "error_code": exc.code,
                    "error_message": exc.message,
                },
            )

    @router.post("/api/v1/events/{event_id}/participants/prepare")
    def prepare_event_participants(event_id: str):
        try:
            return container.event_sandbox.prepare_participants(event_id)
        except EventSandboxError as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "event_id": event_id,
                    "error_code": exc.code,
                    "error_message": exc.message,
                },
            )

    @router.post("/api/v1/statements/{statement_id}/style-embedding")
    def build_statement_style_embedding(statement_id: str):
        try:
            return container.style_embedding.build_market_style_embedding(statement_id).to_dict()
        except StyleEmbeddingError as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "statement_id": statement_id,
                    "error_code": exc.code,
                    "error_message": exc.message,
                },
            )

    @router.post("/api/v1/statements/{statement_id}/archetype-seed")
    def build_statement_archetype_seed(statement_id: str):
        try:
            return container.style_embedding.build_archetype_seed(statement_id).to_dict()
        except StyleEmbeddingError as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "statement_id": statement_id,
                    "error_code": exc.code,
                    "error_message": exc.message,
                },
            )

    @router.post("/api/v1/statements/{statement_id}/activation-calibration")
    def build_statement_activation_calibration(statement_id: str):
        try:
            return container.style_embedding.build_activation_calibration(statement_id).to_dict()
        except StyleEmbeddingError as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "statement_id": statement_id,
                    "error_code": exc.code,
                    "error_message": exc.message,
                },
            )

    @router.post("/api/v1/statements/{statement_id}/mirror-agent")
    def build_mirror_agent(statement_id: str):
        try:
            return container.mirror_agent.build_mirror_agent(statement_id).to_dict()
        except MirrorAgentError as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "statement_id": statement_id,
                    "error_code": exc.code,
                    "error_message": exc.message,
                },
            )

    @router.post("/api/v1/statements/{statement_id}/mirror-agent/validation")
    def validate_mirror_agent(statement_id: str):
        try:
            return container.mirror_agent.validate_mirror_agent(statement_id).to_dict()
        except MirrorAgentError as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "statement_id": statement_id,
                    "error_code": exc.code,
                    "error_message": exc.message,
                },
            )

    @router.post("/api/v1/statements/{statement_id}/distribution-calibration")
    def build_distribution_calibration(statement_id: str):
        return container.calibration.build_distribution_calibration(statement_id).to_dict()

    @router.post("/api/v1/statements/{statement_id}/weight-feedback")
    def build_weight_feedback(statement_id: str):
        return container.calibration.build_weight_feedback(statement_id).to_dict()

    @router.post("/api/v1/roadmaps/1.6/acceptance-pack")
    def build_roadmap_acceptance_pack():
        try:
            return container.acceptance_pack.build_acceptance_pack().to_dict()
        except AcceptancePackError as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "roadmap_id": "roadmap_1_6",
                    "error_code": exc.code,
                    "error_message": exc.message,
                },
            )

    @router.post("/api/v1/agents")
    def create_agent(payload: AgentCreateRequest, request: Request):
        metadata = container.statement_ingestion.get_statement(payload.statement_id)
        if metadata is None:
            return JSONResponse(
                status_code=404,
                content={
                    "statement_id": payload.statement_id,
                    "error_code": "STATEMENT_NOT_FOUND",
                    "error_message": "Statement metadata not found.",
                },
            )
        profile = container.dna_engine.get_profile(payload.statement_id)
        if profile is None:
            return JSONResponse(
                status_code=404,
                content={
                    "statement_id": payload.statement_id,
                    "error_code": "PROFILE_NOT_FOUND",
                    "error_message": "Profile must be generated before agent creation.",
                },
            )
        result = container.agent_registry.create_agent(
            payload,
            profile=profile,
            profile_path=str(container.dna_engine.profile_root / f"{payload.statement_id}.json"),
            public_base_url=str(request.base_url).rstrip("/"),
        )
        return asdict(result)

    @router.post("/api/v1/statements/{statement_id}/parse")
    def parse_statement(statement_id: str):
        metadata = container.statement_ingestion.get_statement(statement_id)
        if metadata is None:
            return JSONResponse(
                status_code=404,
                content={
                    "statement_id": statement_id,
                    "error_code": "STATEMENT_NOT_FOUND",
                    "error_message": "Statement metadata not found.",
                },
            )
        try:
            if metadata.upload_status == "uploaded":
                container.statement_ingestion.transition_status(statement_id=statement_id, next_status="parsing")
                metadata = container.statement_ingestion.get_statement(statement_id) or metadata
            result = container.statement_parser.parse_statement(metadata)
            final_status = "parsed" if result.failed_records == 0 else "failed"
            container.statement_ingestion.transition_status(
                statement_id=statement_id,
                next_status=final_status,
                error_code=result.error_code,
                error_message=result.error_message,
            )
            refreshed = container.statement_ingestion.get_statement(statement_id)
            return {
                **asdict(result),
                "final_status": refreshed.upload_status if refreshed else final_status,
            }
        except (StatementParseError, InvalidStatementTransitionError) as exc:
            error_code = getattr(exc, "code", "STATEMENT_PARSE_FAILED")
            error_message = getattr(exc, "message", str(exc))
            status_code = getattr(exc, "status_code", 400)
            try:
                container.statement_ingestion.transition_status(
                    statement_id=statement_id,
                    next_status="failed",
                    error_code=error_code,
                    error_message=error_message,
                )
            except Exception:
                pass
            return JSONResponse(
                status_code=status_code,
                content={
                    "statement_id": statement_id,
                    "error_code": error_code,
                    "error_message": error_message,
                },
            )

    @router.post("/api/v1/statements/{statement_id}/status")
    def update_statement_status(statement_id: str, payload: StatementStatusUpdateRequest):
        try:
            updated = container.statement_ingestion.transition_status(
                statement_id=statement_id,
                next_status=payload.next_status,
                error_code=payload.error_code,
                error_message=payload.error_message,
            )
        except FileNotFoundError:
            return JSONResponse(
                status_code=404,
                content={
                    "statement_id": statement_id,
                    "error_code": "STATEMENT_NOT_FOUND",
                    "error_message": "Statement metadata not found.",
                },
            )
        except InvalidStatementTransitionError as exc:
            return JSONResponse(
                status_code=400,
                content={
                    "statement_id": statement_id,
                    "error_code": "STATEMENT_INVALID_TRANSITION",
                    "error_message": str(exc),
                },
            )
        return asdict(updated)

    @router.post("/api/v1/agents/{agent_id}/heartbeat")
    def heartbeat(agent_id: str, payload: HeartbeatRequest):
        return container.agent_registry.heartbeat(agent_id, payload)

    @router.post("/api/v1/actions/submit")
    def submit_actions(payload: SubmitActionRequest):
        return container.simulation_ledger.submit_actions(payload)


    @router.post("/api/v1/participants/variants")
    def participant_variants():
        return {"variants": [item.to_dict() for item in container.participant_registry.list_primary_variants()]}

    @router.post("/api/v1/participants/variants/{participant_family}")
    def participant_variant_detail(participant_family: str):
        variant = container.participant_registry.get_primary_variant(participant_family)
        if variant is None:
            return JSONResponse(
                status_code=404,
                content={"participant_family": participant_family, "status": "not_found"},
            )
        return variant.to_dict()



    @router.post("/api/v1/participants/registry")
    def participant_registry_defaults():
        return container.participant_registry.snapshot().to_dict()

    @router.post("/api/v1/participants/registry/{participant_family}")
    def participant_registry_detail(participant_family: str):
        entry = container.participant_registry.get_registry_entry(participant_family)
        if entry is None:
            return JSONResponse(
                status_code=404,
                content={"participant_family": participant_family, "status": "not_found"},
            )
        return entry.to_dict()



    @router.post("/api/v1/events/{event_id}/belief-graph")
    def build_belief_graph(event_id: str):
        try:
            return asdict(container.belief_graph.build_snapshot(event_id))
        except BeliefGraphError as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "event_id": event_id,
                    "error_code": exc.code,
                    "error_message": exc.message,
                },
            )



    @router.post("/api/v1/events/{event_id}/scenarios")
    def build_scenarios(event_id: str):
        try:
            return asdict(container.scenario_engine.build_scenarios(event_id))
        except ScenarioEngineError as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "event_id": event_id,
                    "error_code": exc.code,
                    "error_message": exc.message,
                },
            )



    @router.post("/api/v1/events/{event_id}/simulation/prepare")
    def prepare_simulation(event_id: str):
        try:
            return container.event_simulation.prepare_run(event_id).to_dict()
        except EventSimulationError as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "event_id": event_id,
                    "error_code": exc.code,
                    "error_message": exc.message,
                },
            )

    @router.post("/api/v1/events/{event_id}/simulation/run")
    def run_simulation(event_id: str):
        try:
            return container.event_simulation.run_simulation(event_id).to_dict()
        except EventSimulationError as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "event_id": event_id,
                    "error_code": exc.code,
                    "error_message": exc.message,
                },
            )

    @router.post("/api/v1/events/{event_id}/simulation/continue-day")
    def continue_simulation_day(event_id: str):
        try:
            return container.event_sandbox.continue_simulation_day(event_id)
        except EventSandboxError as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "event_id": event_id,
                    "error_code": exc.code,
                    "error_message": exc.message,
                },
            )
        except EventSimulationError as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "event_id": event_id,
                    "error_code": exc.code,
                    "error_message": exc.message,
                },
            )

    @router.post("/api/v1/events/{event_id}/simulate")
    def simulate_event(event_id: str):
        try:
            return container.event_sandbox.simulate_event(event_id)
        except EventSandboxError as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "event_id": event_id,
                    "error_code": exc.code,
                    "error_message": exc.message,
                },
            )
        except EventSimulationError as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "event_id": event_id,
                    "error_code": exc.code,
                    "error_message": exc.message,
                },
            )

    @router.post("/api/v1/events/{event_id}/workbench/ask")
    def workbench_ask(event_id: str, payload: WorkbenchAskRequest):
        return container.workbench.ask_workbench(event_id, payload)

    @router.post("/api/v1/events/{event_id}/counterfactual")
    def workbench_counterfactual(event_id: str, payload: WorkbenchAskRequest):
        forced_payload = WorkbenchAskRequest(
            question=payload.question,
            ask_type="counterfactual",
            clone_id=payload.clone_id,
            round_id=payload.round_id,
            transition_id=payload.transition_id,
        )
        return container.workbench.ask_workbench(event_id, forced_payload)

    @router.post("/api/v1/events/{event_id}/outcomes")
    def record_outcome(event_id: str, payload: OutcomeReviewWriteRequest):
        try:
            return container.outcome_review.record_outcome(event_id, payload).to_dict()
        except OutcomeReviewError as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "event_id": event_id,
                    "error_code": exc.code,
                    "error_message": exc.message,
                },
            )


    return router

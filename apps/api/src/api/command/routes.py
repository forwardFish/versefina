from __future__ import annotations

from dataclasses import asdict

from infra.http import APIRouter, File, Form, JSONResponse, UploadFile
from modules.statements.parser_service import StatementParseError
from modules.statements.service import StatementUploadValidationError
from modules.statements.status_machine import InvalidStatementTransitionError
from schemas.command import (
    AgentCreateRequest,
    AgentRegisterRequest,
    HeartbeatRequest,
    StatementStatusUpdateRequest,
    StatementUploadRequest,
    SubmitActionRequest,
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

    @router.post("/api/v1/agents")
    def create_agent(payload: AgentCreateRequest):
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

    return router

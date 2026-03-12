from __future__ import annotations

from dataclasses import dataclass

from schemas.common import AcceptedResponse
from schemas.command import StatementUploadRequest


@dataclass(slots=True)
class DNAEngineService:
    def ingest_statement(self, payload: StatementUploadRequest) -> AcceptedResponse:
        return AcceptedResponse(status="accepted", task_id=f"statement::{payload.statement_id}")

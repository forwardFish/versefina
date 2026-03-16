from __future__ import annotations

import uuid

from infra.storage.object_store import LocalObjectStore, build_statement_object_key
from modules.statements.file_detection import StatementFileDetectionError, detect_statement_file_type
from modules.statements.repository import StatementMetadataRepository, utc_now_iso
from schemas.command import StatementMetadata, StatementUploadRequest, StatementUploadResponse


class StatementUploadValidationError(ValueError):
    def __init__(self, *, code: str, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class StatementIngestionService:
    def __init__(
        self,
        *,
        object_store: LocalObjectStore,
        metadata_repository: StatementMetadataRepository,
        max_upload_bytes: int,
    ) -> None:
        self.object_store = object_store
        self.metadata_repository = metadata_repository
        self.max_upload_bytes = max_upload_bytes

    def validate_upload(self, payload: StatementUploadRequest):
        if payload.byte_size <= 0:
            raise StatementUploadValidationError(
                code="STATEMENT_FILE_EMPTY",
                message="Statement file must not be empty.",
            )
        if payload.byte_size > self.max_upload_bytes:
            raise StatementUploadValidationError(
                code="STATEMENT_FILE_TOO_LARGE",
                message=f"Statement file exceeds the {self.max_upload_bytes} byte upload limit.",
            )
        try:
            return detect_statement_file_type(file_name=payload.file_name, content_type=payload.content_type)
        except StatementFileDetectionError as exc:
            raise StatementUploadValidationError(code=exc.code, message=exc.message) from exc

    def ingest_statement(self, payload: StatementUploadRequest, file_bytes: bytes) -> StatementUploadResponse:
        detection = self.validate_upload(payload)
        statement_id = payload.statement_id or f"stmt_{uuid.uuid4().hex[:12]}"
        object_key = build_statement_object_key(payload.owner_id, statement_id, payload.file_name)
        try:
            stored = self.object_store.put_bytes(object_key=object_key, data=file_bytes)
        except Exception as exc:
            raise StatementUploadValidationError(
                code="STATEMENT_STORAGE_WRITE_FAILED",
                message=f"Failed to persist statement object: {exc}",
                status_code=500,
            ) from exc

        try:
            timestamp = utc_now_iso()
            metadata = StatementMetadata(
                statement_id=statement_id,
                owner_id=payload.owner_id,
                market=payload.market,
                file_name=payload.file_name,
                content_type=detection.normalized_content_type,
                detected_file_type=detection.detected_file_type,
                parser_key=detection.parser_key,
                byte_size=payload.byte_size,
                bucket=stored.bucket,
                object_key=stored.object_key,
                upload_status="uploaded",
                created_at=timestamp,
                updated_at=timestamp,
            )
            self.metadata_repository.save(metadata)
        except Exception as exc:
            self.object_store.delete(object_key=object_key)
            raise StatementUploadValidationError(
                code="STATEMENT_METADATA_PERSIST_FAILED",
                message=f"Failed to persist statement metadata: {exc}",
                status_code=500,
            ) from exc

        return StatementUploadResponse(
            statement_id=statement_id,
            upload_status="uploaded",
            object_key=stored.object_key,
            bucket=stored.bucket,
            file_name=payload.file_name,
            byte_size=payload.byte_size,
            market=payload.market,
        )

    def reject_upload(
        self,
        *,
        owner_id: str,
        file_name: str,
        content_type: str,
        byte_size: int,
        market: str,
        statement_id: str | None,
        code: str,
        message: str,
    ) -> StatementUploadResponse:
        return StatementUploadResponse(
            statement_id=statement_id or f"stmt_rejected_{uuid.uuid4().hex[:8]}",
            upload_status="rejected",
            object_key=None,
            bucket=self.object_store.bucket,
            file_name=file_name,
            byte_size=byte_size,
            market=market,
            error_code=code,
            error_message=message,
        )

    def get_statement(self, statement_id: str) -> StatementMetadata | None:
        return self.metadata_repository.get(statement_id)

    def transition_status(
        self,
        *,
        statement_id: str,
        next_status: str,
        error_code: str | None = None,
        error_message: str | None = None,
    ) -> StatementMetadata:
        return self.metadata_repository.transition_status(
            statement_id,
            next_status,
            error_code=error_code,
            error_message=error_message,
        )

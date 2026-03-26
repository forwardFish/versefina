from __future__ import annotations

from dataclasses import asdict
from datetime import UTC, datetime
import json
from pathlib import Path
import re

from domain.event_casebook.service import EventCasebookService
from domain.event_structuring.service import EventStructuringService
from domain.theme_mapping.service import ThemeMappingService
from schemas.command import EventCreateRequest, EventCreateResponse, EventPrepareResponse
from schemas.event import EventRecord


_WHITELIST_HINTS = ("涨价", "价格上涨", "供给", "停产", "限产", "冲击", "supply", "price shock")


class EventIngestionError(Exception):
    def __init__(self, *, code: str, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class EventIngestionService:
    def __init__(
        self,
        runtime_root: Path,
        structuring_service: EventStructuringService,
        theme_mapping_service: ThemeMappingService,
        casebook_service: EventCasebookService,
    ) -> None:
        self.runtime_root = runtime_root
        self.record_root = runtime_root / "records"
        self.record_root.mkdir(parents=True, exist_ok=True)
        self.structuring_service = structuring_service
        self.theme_mapping_service = theme_mapping_service
        self.casebook_service = casebook_service

    def ingest_event(self, payload: EventCreateRequest) -> EventCreateResponse:
        body = payload.body.strip()
        if not body:
            raise EventIngestionError(code="EVENT_TEXT_REQUIRED", message="Event text must not be empty.")
        if not self._is_whitelisted(body):
            raise EventIngestionError(
                code="EVENT_NOT_IN_WHITELIST",
                message="Only supply-chain price shock events can enter the P0 workflow.",
            )
        event_id = self._build_event_id(payload)
        record = EventRecord(
            event_id=event_id,
            title=(payload.title or body[:48]).strip(),
            body=body,
            source=payload.source,
            event_time=payload.event_time or datetime.now(UTC).isoformat(),
            status="raw",
        )
        self._write_record(record)
        structure = self.structuring_service.structure_event(record)
        mapping = self.theme_mapping_service.map_structure(structure)
        self.casebook_service.write_casebook(record=record, structure=structure, mapping=mapping, status="structured")
        return EventCreateResponse(
            event_id=record.event_id,
            event_type=structure.event_type,
            status="structured",
            structure=asdict(structure),
            mapping=asdict(mapping),
        )

    def prepare_event(self, event_id: str) -> EventPrepareResponse:
        casebook = self.casebook_service.mark_prepared(event_id)
        record = self.load_record(event_id)
        if record is not None:
            prepared_record = EventRecord(
                event_id=record.event_id,
                title=record.title,
                body=record.body,
                source=record.source,
                event_time=record.event_time,
                status="prepared",
            )
            self._write_record(prepared_record)
        return EventPrepareResponse(event_id=event_id, status="prepared", casebook=asdict(casebook))

    def load_record(self, event_id: str) -> EventRecord | None:
        target_path = self.record_root / f"{event_id}.json"
        if not target_path.exists():
            return None
        payload = json.loads(target_path.read_text(encoding="utf-8"))
        return EventRecord(**payload)

    def _build_event_id(self, payload: EventCreateRequest) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", payload.title.lower()).strip("-") or "event"
        return f"evt-{slug}-{datetime.now(UTC).strftime('%Y%m%d%H%M%S%f')}"

    def _is_whitelisted(self, text: str) -> bool:
        lowered = text.lower()
        return any(token in lowered for token in _WHITELIST_HINTS)

    def _write_record(self, record: EventRecord) -> None:
        target_path = self.record_root / f"{record.event_id}.json"
        target_path.write_text(json.dumps(asdict(record), ensure_ascii=False, indent=2), encoding="utf-8")

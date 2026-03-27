from __future__ import annotations

from dataclasses import asdict
from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any

from domain.event_ingestion.service import EventIngestionError, EventIngestionService
from domain.event_sandbox.service import EventSandboxError, EventSandboxService
from schemas.command import FinahuntEventImportRequest, FinahuntEventImportResponse
from schemas.event import EventLineagePayload


class FinahuntIngestionError(Exception):
    def __init__(self, *, code: str, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class FinahuntEventIngestionService:
    def __init__(
        self,
        *,
        finahunt_runtime_root: Path,
        event_runtime_root: Path,
        event_ingestion: EventIngestionService,
        event_sandbox: EventSandboxService,
    ) -> None:
        self.finahunt_runtime_root = finahunt_runtime_root
        self.event_ingestion = event_ingestion
        self.event_sandbox = event_sandbox
        self.lineage_root = event_runtime_root / "lineage"
        self.lineage_root.mkdir(parents=True, exist_ok=True)

    def import_event(self, payload: FinahuntEventImportRequest) -> FinahuntEventImportResponse:
        run_root = self._resolve_run_root(payload.run_id)
        manifest = self._load_json(run_root / "manifest.json")
        ranked_feed = self._load_json(run_root / "ranked_result_feed.json")
        workbench = self._load_json(run_root / "daily_message_workbench.json")
        ranked_items = ranked_feed if isinstance(ranked_feed, list) else []
        messages = list(workbench.get("messages") or []) if isinstance(workbench, dict) else []
        if not ranked_items:
            raise FinahuntIngestionError(
                code="FINAHUNT_RANKED_FEED_EMPTY",
                message="No ranked finahunt events are available for import.",
                status_code=404,
            )

        candidate = self._select_candidate(ranked_items, messages, payload)
        source_message = candidate["message"]
        source_record = source_message.get("message") or {}
        title = self._repair_text(str(source_record.get("title") or candidate["rank_item"].get("top_evidence", [{}])[0].get("title") or "真实事件导入"))
        summary = self._repair_text(
            str(
                source_record.get("message_text")
                or source_record.get("summary")
                or candidate["rank_item"].get("core_narrative")
                or candidate["rank_item"].get("catalyst_summary")
                or title
            )
        )
        source_name = self._repair_text(str(source_record.get("source_name") or "Finahunt"))
        source_priority = self._repair_text(str(source_record.get("source_priority") or ""))
        primary_theme = self._repair_text(
            str(candidate["impact"].get("primary_theme") or candidate["rank_item"].get("theme_name") or "")
        )
        created = self.event_ingestion.ingest_external_event(
            title=title,
            body=summary,
            source=f"finahunt:{source_name or 'runtime'}",
            event_time=str(source_record.get("event_time") or source_record.get("occurred_at") or manifest.get("created_at") or datetime.now(UTC).isoformat()),
        )
        lineage = EventLineagePayload(
            event_id=created.event_id,
            status="ready",
            finahunt_run_id=str(manifest.get("run_id") or run_root.name),
            finahunt_trace_id=str(manifest.get("trace_id") or ""),
            source_artifact=str(candidate["artifact_name"]),
            source_event_id=str(source_record.get("message_id") or ""),
            source_title=title,
            source_name=source_name,
            source_url=str(source_record.get("source_url") or ""),
            source_priority=source_priority,
            primary_theme=primary_theme,
            ranking_context={
                "rank_position": candidate["rank_item"].get("rank_position"),
                "relevance_score": candidate["rank_item"].get("relevance_score"),
                "theme_name": self._repair_text(str(candidate["rank_item"].get("theme_name") or "")),
                "fermentation_phase": self._repair_text(str(candidate["rank_item"].get("fermentation_phase") or "")),
                "impact_direction": self._repair_text(str(candidate["impact"].get("impact_direction") or "")),
            },
            message_snapshot={
                "event_subject": self._repair_text(str(source_record.get("event_subject") or "")),
                "summary": self._repair_text(str(source_record.get("summary") or "")),
                "related_themes": [self._repair_text(str(item)) for item in list(source_record.get("related_themes") or [])],
                "related_industries": [self._repair_text(str(item)) for item in list(source_record.get("related_industries") or [])],
            },
            imported_at=datetime.now(UTC).isoformat(),
        )
        self._write_lineage(lineage)

        structure_status = created.status
        participant_status = "skipped"
        simulation_status = "skipped"
        if payload.auto_structure_prepare_simulate:
            prepare_payload = self.event_sandbox.prepare_participants(created.event_id)
            participant_status = str(prepare_payload.get("status") or "prepared")
            simulation_payload = self.event_sandbox.simulate_event(created.event_id)
            simulation_status = str(simulation_payload.get("status") or "completed")

        return FinahuntEventImportResponse(
            event_id=created.event_id,
            status="ready",
            run_id=str(manifest.get("run_id") or run_root.name),
            source_event_id=str(source_record.get("message_id") or ""),
            lineage=lineage.to_dict(),
            structure_status=structure_status,
            participant_status=participant_status,
            simulation_status=simulation_status,
        )

    def load_lineage(self, event_id: str) -> EventLineagePayload | None:
        target_path = self.lineage_root / f"{event_id}.json"
        if not target_path.exists():
            return None
        return EventLineagePayload(**json.loads(target_path.read_text(encoding="utf-8")))

    def _resolve_run_root(self, requested_run_id: str | None) -> Path:
        if requested_run_id:
            target = self.finahunt_runtime_root / requested_run_id
            if target.exists():
                return target
            raise FinahuntIngestionError(
                code="FINAHUNT_RUN_NOT_FOUND",
                message=f"Finahunt run {requested_run_id} was not found.",
                status_code=404,
            )
        candidates = sorted(
            [item for item in self.finahunt_runtime_root.iterdir() if item.is_dir() and item.name.startswith("run-")],
            key=lambda item: item.stat().st_mtime,
            reverse=True,
        )
        if not candidates:
            raise FinahuntIngestionError(
                code="FINAHUNT_RUNTIME_EMPTY",
                message="No finahunt runtime artifacts are available.",
                status_code=404,
            )
        return candidates[0]

    def _select_candidate(
        self,
        ranked_items: list[dict[str, Any]],
        messages: list[dict[str, Any]],
        payload: FinahuntEventImportRequest,
    ) -> dict[str, Any]:
        selected_rank_item = ranked_items[0]
        if payload.rank_position is not None:
            match = next((item for item in ranked_items if int(item.get("rank_position") or 0) == payload.rank_position), None)
            if match is None:
                raise FinahuntIngestionError(
                    code="FINAHUNT_RANK_POSITION_NOT_FOUND",
                    message=f"Rank position {payload.rank_position} was not found in the finahunt feed.",
                    status_code=404,
                )
            selected_rank_item = match

        selected_message_id = payload.message_id
        if not selected_message_id:
            top_evidence = list(selected_rank_item.get("top_evidence") or [])
            selected_message_id = str((top_evidence[0] if top_evidence else {}).get("event_id") or "")

        selected_message = next(
            (item for item in messages if str((item.get("message") or {}).get("message_id") or "") == selected_message_id),
            None,
        )
        if selected_message is None and messages:
            selected_message = messages[0]
        if selected_message is None:
            selected_message = {"message": {}}

        return {
            "artifact_name": "ranked_result_feed.json",
            "rank_item": selected_rank_item,
            "message": selected_message,
            "impact": selected_message.get("impact") or {},
        }

    def _write_lineage(self, lineage: EventLineagePayload) -> None:
        target_path = self.lineage_root / f"{lineage.event_id}.json"
        target_path.write_text(json.dumps(asdict(lineage), ensure_ascii=False, indent=2), encoding="utf-8")

    def _load_json(self, path: Path) -> Any:
        if not path.exists():
            raise FinahuntIngestionError(
                code="FINAHUNT_ARTIFACT_MISSING",
                message=f"Required finahunt artifact {path.name} was not found.",
                status_code=404,
            )
        return json.loads(path.read_text(encoding="utf-8"))

    def _repair_text(self, value: str) -> str:
        if not value:
            return value
        if not self._looks_mojibake(value):
            return value
        try:
            repaired = value.encode("gb18030").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            return value
        return repaired if repaired.strip() else value

    def _looks_mojibake(self, value: str) -> bool:
        markers = ("閿", "锛", "銆", "鏈", "鏉", "浠", "绾", "鍐", "闆", "鍙", "鎴", "瑙")
        return any(marker in value for marker in markers)

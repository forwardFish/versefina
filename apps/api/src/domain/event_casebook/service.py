from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path

from schemas.event import EventCasebookEntry, EventRecord, EventStructure, ThemeMappingResult


class EventCasebookService:
    def __init__(self, runtime_root: Path) -> None:
        self.runtime_root = runtime_root
        self.casebook_root = runtime_root / "casebook"
        self.casebook_root.mkdir(parents=True, exist_ok=True)

    def write_casebook(
        self,
        *,
        record: EventRecord,
        structure: EventStructure,
        mapping: ThemeMappingResult,
        status: str,
    ) -> EventCasebookEntry:
        entry = EventCasebookEntry(
            event_id=record.event_id,
            record=asdict(record),
            structure=asdict(structure),
            mapping=asdict(mapping),
            status=status,
        )
        target_path = self.casebook_root / f"{record.event_id}.json"
        target_path.write_text(json.dumps(asdict(entry), ensure_ascii=False, indent=2), encoding="utf-8")
        return entry

    def mark_prepared(self, event_id: str) -> EventCasebookEntry:
        entry = self.load_casebook(event_id)
        if entry is None:
            raise FileNotFoundError(f"Casebook entry not found: {event_id}")
        updated = EventCasebookEntry(
            event_id=entry.event_id,
            record=dict(entry.record),
            structure=dict(entry.structure),
            mapping=dict(entry.mapping),
            status="prepared",
        )
        target_path = self.casebook_root / f"{event_id}.json"
        target_path.write_text(json.dumps(asdict(updated), ensure_ascii=False, indent=2), encoding="utf-8")
        return updated

    def load_casebook(self, event_id: str) -> EventCasebookEntry | None:
        target_path = self.casebook_root / f"{event_id}.json"
        if not target_path.exists():
            return None
        payload = json.loads(target_path.read_text(encoding="utf-8"))
        return EventCasebookEntry(**payload)

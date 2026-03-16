from __future__ import annotations

from dataclasses import asdict, replace
from datetime import datetime, timezone
import json
from pathlib import Path

from modules.statements.status_machine import validate_statement_transition
from schemas.command import StatementMetadata


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class StatementMetadataRepository:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def get(self, statement_id: str) -> StatementMetadata | None:
        target = self.root / f"{statement_id}.json"
        if not target.exists():
            return None
        payload = json.loads(target.read_text(encoding="utf-8"))
        return StatementMetadata(**payload)

    def save(self, metadata: StatementMetadata) -> StatementMetadata:
        target = self.root / f"{metadata.statement_id}.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(asdict(metadata), ensure_ascii=False, indent=2), encoding="utf-8")
        return metadata

    def transition_status(
        self,
        statement_id: str,
        next_status: str,
        *,
        error_code: str | None = None,
        error_message: str | None = None,
    ) -> StatementMetadata:
        current = self.get(statement_id)
        if current is None:
            raise FileNotFoundError(f"Statement metadata not found: {statement_id}")
        validate_statement_transition(current.upload_status, next_status)
        updated = replace(
            current,
            upload_status=next_status,
            updated_at=utc_now_iso(),
            error_code=error_code,
            error_message=error_message,
        )
        return self.save(updated)

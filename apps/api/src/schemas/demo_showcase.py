from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class RuntimeShowcaseResponse:
    generated_at: str
    event_demo: dict[str, Any] = field(default_factory=dict)
    statement_demo: dict[str, Any] = field(default_factory=dict)
    acceptance_demo: dict[str, Any] = field(default_factory=dict)
    source_paths: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

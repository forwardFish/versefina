from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class ScenarioCase:
    scenario_id: str
    thesis: str
    first_movers: list[str] = field(default_factory=list)
    followers: list[str] = field(default_factory=list)
    watchpoints: list[str] = field(default_factory=list)
    invalidation_conditions: list[str] = field(default_factory=list)
    confidence: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

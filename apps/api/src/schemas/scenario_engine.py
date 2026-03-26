from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from schemas.scenario import ScenarioCase


@dataclass(frozen=True, slots=True)
class ScenarioEngineResult:
    event_id: str
    dominant_scenario: str
    graph_status: str
    graph_metrics: dict[str, int | float | str] = field(default_factory=dict)
    scenarios: list[ScenarioCase] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

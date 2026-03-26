from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class OutcomeReview:
    event_id: str
    horizon: str
    sector_performance: str
    leader_performance: str
    expansion_status: str
    sentiment_status: str
    dominant_scenario_actual: str
    score_label: str
    predicted_scenario: str = ""
    status: str = "ready"
    event_type: str = ""
    source_run_id: str = ""
    analyst_note: str = ""
    recorded_at: str = ""
    failure_reasons: list[str] = field(default_factory=list)
    supporting_evidence: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

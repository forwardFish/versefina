from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from schemas.report import ReportCard, ReviewReport


@dataclass(frozen=True, slots=True)
class ReportingBundle:
    event_id: str
    report_card: ReportCard
    review_report: ReviewReport
    why_context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class WhyReport:
    event_id: str
    status: str
    answer: str
    dominant_scenario: str = ""
    actual_outcome: str = ""
    score_label: str = ""
    evidence: dict[str, Any] = field(default_factory=dict)
    gaps: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

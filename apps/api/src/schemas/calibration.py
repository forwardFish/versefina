from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class ParticipantSegmentStat:
    event_type: str
    participant_family: str
    sample_size: int
    hit_rate: float
    failure_rate: float
    insufficient_sample: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class BeliefPatternStat:
    pattern: str
    hit_count: int
    failure_count: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class DistributionCalibrationSummary:
    statement_id: str
    status: str
    participant_segments: list[ParticipantSegmentStat] = field(default_factory=list)
    belief_patterns: list[BeliefPatternStat] = field(default_factory=list)
    source_validation: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ParticipantWeightRecommendation:
    participant_family: str
    current_weight: float
    suggested_weight: float
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ScenarioWeightRecommendation:
    scenario_id: str
    current_weight: float
    suggested_weight: float
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class CalibrationFeedback:
    statement_id: str
    status: str
    apply_allowed: bool
    participant_weights: list[ParticipantWeightRecommendation] = field(default_factory=list)
    scenario_weights: list[ScenarioWeightRecommendation] = field(default_factory=list)
    review_required: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class ParticipantReliability:
    participant_family: str
    sample_size: int
    direction_correct_score: float
    early_detection_score: float
    invalidation_detection_score: float
    last_score_label: str
    ability_tags: list[str] = field(default_factory=list)
    low_sample_size: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ReliabilitySummary:
    event_id: str
    event_type: str
    status: str
    participants: list[ParticipantReliability] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

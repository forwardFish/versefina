from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class ParticipantInfluenceEdge:
    source_participant_id: str
    source_participant_family: str
    target_participant_id: str
    target_participant_family: str
    round_id: str
    order: int
    influence_type: str
    polarity: str
    strength: float
    reason: str
    lag_windows: int = 1
    activation_condition: str = ""
    expiration_condition: str = ""
    effect_on: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class InfluenceGraphRound:
    event_id: str
    round_id: str
    order: int
    market_state: str
    edges: list[ParticipantInfluenceEdge] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class InfluenceGraphPayload:
    event_id: str
    status: str
    latest_round_id: str = ""
    rounds: list[InfluenceGraphRound] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

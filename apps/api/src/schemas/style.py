from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class MarketStyleEmbedding:
    statement_id: str
    status: str
    holding_period_distribution: dict[str, float] = field(default_factory=dict)
    momentum_preference_score: float = 0.0
    mean_reversion_score: float = 0.0
    concentration_score: float = 0.0
    reaction_latency_profile: dict[str, Any] = field(default_factory=dict)
    feature_vector: dict[str, float] = field(default_factory=dict)
    low_confidence: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ArchetypeSeed:
    statement_id: str
    status: str
    archetype_name: str
    participant_family: str
    reaction_rules: list[str] = field(default_factory=list)
    participant_profile: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    low_confidence: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ParticipantActivationRule:
    event_type: str
    participant_family: str
    activation_weight: float
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ParticipantActivationCalibration:
    statement_id: str
    status: str
    source_archetype: str
    default_activation: bool = False
    rules: list[ParticipantActivationRule] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

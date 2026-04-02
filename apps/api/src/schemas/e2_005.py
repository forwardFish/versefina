from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class ParticipantRegistryEntry:
    participant_family: str
    style_variant: str
    authority_weight: float
    risk_budget_profile: str
    influence_weight: float = 0.0
    capital_bucket: str = ""
    capital_base: float = 0.0
    max_event_exposure: float = 0.0
    reaction_latency: int = 0
    entry_threshold: float = 0.0
    add_threshold: float = 0.0
    reduce_threshold: float = 0.0
    exit_threshold: float = 0.0
    notes: list[str] = field(default_factory=list)
    calibration_status: str = "default"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ParticipantRegistrySnapshot:
    entries: list[ParticipantRegistryEntry] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

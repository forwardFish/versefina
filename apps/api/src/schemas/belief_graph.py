from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class BeliefGraphNode:
    participant_id: str
    participant_family: str
    stance: str
    authority_weight: float
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class BeliefGraphSnapshot:
    event_id: str
    status: str
    participant_count: int
    key_supporters: list[str] = field(default_factory=list)
    key_opponents: list[str] = field(default_factory=list)
    consensus_signals: list[str] = field(default_factory=list)
    divergence_signals: list[str] = field(default_factory=list)
    nodes: list[BeliefGraphNode] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

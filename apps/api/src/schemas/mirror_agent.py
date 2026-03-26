from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class MirrorAgent:
    statement_id: str
    status: str
    archetype_name: str
    participant_family: str
    style_embedding: dict[str, Any] = field(default_factory=dict)
    activation_calibration: dict[str, Any] = field(default_factory=dict)
    profile: dict[str, Any] = field(default_factory=dict)
    evidence: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class MirrorAgentValidation:
    statement_id: str
    status: str
    risk: str
    noise: str
    hold: str
    grading: str
    provisional: bool = False
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

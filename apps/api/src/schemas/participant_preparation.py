from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from schemas.participant import ParticipantOutput


@dataclass(frozen=True, slots=True)
class ParticipantRoster:
    event_id: str
    status: str
    participants: list[ParticipantOutput] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    activation_basis: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

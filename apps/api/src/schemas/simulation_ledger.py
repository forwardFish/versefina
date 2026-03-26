from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class SimulationActionLogEntry:
    event_id: str
    run_id: str
    round_id: str
    order: int
    participant_id: str
    actor_id: str
    target_id: str
    action_name: str
    action_type: str
    confidence: float
    reason_code: str
    state_before: str
    state_after: str
    reason_codes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SimulationActionLogView:
    event_id: str
    status: str
    run_id: str = ""
    path: str = ""
    entries: list[SimulationActionLogEntry] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SimulationStateSnapshot:
    event_id: str
    run_id: str
    round_id: str
    order: int
    participant_states: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SimulationStateSnapshotView:
    event_id: str
    status: str
    run_id: str = ""
    snapshots: list[SimulationStateSnapshot] = field(default_factory=list)
    paths: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

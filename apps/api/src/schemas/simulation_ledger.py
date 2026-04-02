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
    execution_window: str = ""
    day_index: int = 0
    trade_date: str = ""
    target_symbol: str = ""
    order_side: str = ""
    order_value: float = 0.0
    order_value_range_min: float = 0.0
    order_value_range_max: float = 0.0
    reference_price: float = 0.0
    lot_size: int = 0
    trade_quantity: float = 0.0
    position_before: float = 0.0
    position_after: float = 0.0
    position_qty_before: float = 0.0
    position_qty_after: float = 0.0
    cash_before: float = 0.0
    cash_after: float = 0.0
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
    day_index: int = 0
    trade_date: str = ""
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

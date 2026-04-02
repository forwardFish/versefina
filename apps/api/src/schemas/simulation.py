from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


SIMULATION_ACTION_PROTOCOL = (
    "IGNORE",
    "WATCH",
    "VALIDATE",
    "INIT_BUY",
    "ADD_BUY",
    "REDUCE",
    "EXIT",
    "BROADCAST_BULL",
    "BROADCAST_BEAR",
)

SIMULATION_ACTION_DISPLAY_TYPES = {
    "IGNORE": "ignore",
    "WATCH": "risk_watch",
    "VALIDATE": "validate",
    "INIT_BUY": "init_buy",
    "ADD_BUY": "add_buy",
    "REDUCE": "reduce",
    "EXIT": "exit",
    "BROADCAST_BULL": "broadcast_bull",
    "BROADCAST_BEAR": "broadcast_bear",
}

SIMULATION_ACTION_STATE_TRANSITIONS = {
    "IGNORE": ("ready", "watching"),
    "WATCH": ("ready", "watching"),
    "VALIDATE": ("watching", "validated"),
    "INIT_BUY": ("ready", "engaged"),
    "ADD_BUY": ("engaged", "accelerating"),
    "REDUCE": ("accelerating", "de_risking"),
    "EXIT": ("de_risking", "exited"),
    "BROADCAST_BULL": ("validated", "broadcasting"),
    "BROADCAST_BEAR": ("validated", "broadcasting"),
}

DEFAULT_SIMULATION_DAYS = 5
MAX_SIMULATION_DAYS = 15
CN_A_LOT_SIZE = 100
DEFAULT_REFERENCE_PRICE = 12.0


@dataclass(frozen=True, slots=True)
class SimulationActionProtocolDefinition:
    action_name: str
    display_action_type: str
    previous_state: str
    next_state: str
    target_required: bool
    description: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


SIMULATION_ACTION_PROTOCOL_DEFINITIONS = tuple(
    SimulationActionProtocolDefinition(
        action_name=action_name,
        display_action_type=SIMULATION_ACTION_DISPLAY_TYPES[action_name],
        previous_state=SIMULATION_ACTION_STATE_TRANSITIONS[action_name][0],
        next_state=SIMULATION_ACTION_STATE_TRANSITIONS[action_name][1],
        target_required=action_name
        not in {"IGNORE", "WATCH", "VALIDATE", "BROADCAST_BULL", "BROADCAST_BEAR"},
        description=f"{action_name} is part of the clone-level closed-loop action vocabulary.",
    )
    for action_name in SIMULATION_ACTION_PROTOCOL
)


def normalize_simulation_action_name(action_name: str) -> str:
    normalized = str(action_name or "").strip().upper()
    if normalized not in SIMULATION_ACTION_PROTOCOL:
        supported = ", ".join(SIMULATION_ACTION_PROTOCOL)
        raise ValueError(f"Unsupported simulation action '{action_name}'. Supported actions: {supported}.")
    return normalized


@dataclass(frozen=True, slots=True)
class SimulationParticipantState:
    participant_id: str
    participant_family: str
    style_variant: str
    role: str
    stance: str
    authority_weight: float
    confidence: float
    influence_weight: float = 0.0
    state: str = "ready"
    capital_bucket: str = ""
    capital_base: float = 0.0
    cash_available: float = 0.0
    current_positions: dict[str, float] = field(default_factory=dict)
    current_position_quantities: dict[str, float] = field(default_factory=dict)
    max_event_exposure: float = 0.0
    planned_allocation: float = 0.0
    reaction_latency: int = 0
    entry_threshold: float = 0.0
    add_threshold: float = 0.0
    reduce_threshold: float = 0.0
    exit_threshold: float = 0.0
    trigger_signals: list[str] = field(default_factory=list)
    invalidation_signals: list[str] = field(default_factory=list)
    preferred_execution_windows: list[str] = field(default_factory=list)
    avoid_execution_windows: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    reason_codes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SimulationRoundPlan:
    round_id: str
    order: int
    focus: str
    objective: str
    dominant_scenario: str
    execution_window: str = ""
    day_index: int = 0
    trade_date: str = ""
    is_trading_day: bool = True
    is_incremental_generated: bool = False
    watchpoints: list[str] = field(default_factory=list)
    reason_codes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SimulationParticipantUpdate:
    participant_id: str
    action_type: str
    previous_state: str
    next_state: str
    round_id: str
    actor_id: str = ""
    target_id: str = ""
    action_name: str = ""
    confidence: float = 0.0
    reason_code: str = ""
    reason_codes: list[str] = field(default_factory=list)
    execution_window: str = ""
    day_index: int = 0
    trade_date: str = ""
    target_symbol: str = ""
    order_side: str = ""
    order_value: float = 0.0
    order_value_range_min: float = 0.0
    order_value_range_max: float = 0.0
    reference_price: float = 0.0
    reference_price_source: str = ""
    lot_size: int = 0
    trade_quantity: float = 0.0
    trade_unit_label: str = "股"
    position_before: float = 0.0
    position_after: float = 0.0
    position_qty_before: float = 0.0
    position_qty_after: float = 0.0
    holding_qty_after: float = 0.0
    cash_before: float = 0.0
    cash_after: float = 0.0
    influenced_by: list[dict[str, Any]] = field(default_factory=list)
    evidence_trace: list[dict[str, Any]] = field(default_factory=list)
    effect_summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SimulationRoundResult:
    round_id: str
    order: int
    focus: str
    objective: str
    status: str
    execution_window: str = ""
    day_index: int = 0
    trade_date: str = ""
    is_trading_day: bool = True
    is_incremental_generated: bool = False
    actions_count: int = 0
    buy_clone_count: int = 0
    sell_clone_count: int = 0
    new_entry_clone_count: int = 0
    exit_clone_count: int = 0
    participant_updates: list[SimulationParticipantUpdate] = field(default_factory=list)
    participant_states: list[dict[str, Any]] = field(default_factory=list)
    influence_edges: list[dict[str, Any]] = field(default_factory=list)
    market_metrics: dict[str, Any] = field(default_factory=dict)
    belief_metrics: dict[str, Any] = field(default_factory=dict)
    reason_codes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SimulationRun:
    run_id: str
    event_id: str
    status: str
    graph_status: str
    dominant_scenario: str
    round_count: int
    participant_states: list[SimulationParticipantState] = field(default_factory=list)
    rounds: list[SimulationRoundPlan] = field(default_factory=list)
    execution_clock: dict[str, Any] = field(default_factory=dict)
    watchpoints: list[str] = field(default_factory=list)
    default_day_count: int = DEFAULT_SIMULATION_DAYS
    generated_day_count: int = 0
    latest_trade_date: str = ""
    created_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SimulationPrepareResult:
    event_id: str
    status: str
    simulation_run: dict[str, Any]
    runner_payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SimulationExecutionResult:
    event_id: str
    status: str
    simulation_run: dict[str, Any]
    round_results: list[dict[str, Any]]
    final_participant_states: list[dict[str, Any]]
    timeline: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SimulationTimelineEntry:
    participant_id: str
    round_id: str
    order: int
    action_type: str
    state_before: str
    state_after: str
    execution_window: str = ""
    day_index: int = 0
    trade_date: str = ""
    target_symbol: str = ""
    order_value: float = 0.0
    trade_quantity: float = 0.0
    reason_codes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SimulationTimelineSummary:
    status: str
    first_move: list[SimulationTimelineEntry] = field(default_factory=list)
    follow_on: list[SimulationTimelineEntry] = field(default_factory=list)
    exit_chain: list[SimulationTimelineEntry] = field(default_factory=list)
    turning_points: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

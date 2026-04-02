from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from schemas.influence_graph import ParticipantInfluenceEdge
from schemas.simulation import DEFAULT_SIMULATION_DAYS


@dataclass(frozen=True, slots=True)
class ParticipantAction:
    participant_id: str
    participant_family: str
    action_type: str
    previous_state: str
    next_state: str
    polarity: str
    action_name: str = ""
    actor_id: str = ""
    target_id: str = ""
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
class BeliefRoundSnapshot:
    event_id: str
    round_id: str
    order: int
    consensus_strength: float
    opposition_strength: float
    divergence_index: float
    day_index: int = 0
    trade_date: str = ""
    net_flow: float = 0.0
    key_supporters: list[str] = field(default_factory=list)
    key_opponents: list[str] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class MarketStateSnapshot:
    event_id: str
    round_id: str
    order: int
    state: str
    active_participant_count: int
    exit_count: int
    follow_on_count: int
    execution_window: str = ""
    day_index: int = 0
    trade_date: str = ""
    net_flow: float = 0.0
    buy_clone_count: int = 0
    sell_clone_count: int = 0
    crowding_score: float = 0.0
    fragility_score: float = 0.0
    dominant_support_chain: list[str] = field(default_factory=list)
    opposition_strength: float = 0.0
    invalidation_hits: int = 0
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ScenarioRoundSnapshot:
    event_id: str
    round_id: str
    order: int
    dominant_scenario: str
    bull_confidence: float
    base_confidence: float
    bear_confidence: float
    summary: str
    day_index: int = 0
    trade_date: str = ""
    watchpoints: list[str] = field(default_factory=list)
    invalidation_conditions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RoundSnapshot:
    event_id: str
    run_id: str
    round_id: str
    order: int
    focus: str
    objective: str
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
    participant_actions: list[ParticipantAction] = field(default_factory=list)
    participant_states: list[dict[str, Any]] = field(default_factory=list)
    influence_edges: list[ParticipantInfluenceEdge] = field(default_factory=list)
    belief_snapshot: BeliefRoundSnapshot | None = None
    market_state: MarketStateSnapshot | None = None
    scenario_snapshot: ScenarioRoundSnapshot | None = None
    turning_point: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SimulationSummaryPayload:
    event_id: str
    status: str
    run_id: str = ""
    dominant_scenario: str = ""
    round_count: int = 0
    latest_market_state: str = ""
    default_day_count: int = DEFAULT_SIMULATION_DAYS
    generated_day_count: int = 0
    latest_trade_date: str = ""
    timeline: dict[str, Any] = field(default_factory=dict)
    top_participants: list[dict[str, Any]] = field(default_factory=list)
    rounds: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ReplayPayload:
    event_id: str
    status: str
    run_id: str = ""
    dominant_scenario: str = ""
    default_day_count: int = DEFAULT_SIMULATION_DAYS
    generated_day_count: int = 0
    can_continue: bool = True
    timeline: dict[str, Any] = field(default_factory=dict)
    rounds: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ValidationPayload:
    event_id: str
    status: str
    report: dict[str, Any] = field(default_factory=dict)
    why: dict[str, Any] = field(default_factory=dict)
    outcomes: dict[str, Any] = field(default_factory=dict)
    reliability: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

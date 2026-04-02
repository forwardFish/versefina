from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class WorkbenchNode:
    node_id: str
    node_type: str
    label: str
    group: str = ""
    highlighted: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class WorkbenchEdge:
    edge_id: str
    edge_type: str
    source: str
    target: str
    label: str = ""
    polarity: str = "neutral"
    strength: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class GraphStageHighlights:
    active_round_id: str = ""
    active_window: str = ""
    active_day_index: int = 0
    active_trade_date: str = ""
    is_incremental_generated: bool = False
    actions_count: int = 0
    buy_clone_count: int = 0
    sell_clone_count: int = 0
    new_entry_clone_count: int = 0
    exit_clone_count: int = 0
    active_clone_ids: list[str] = field(default_factory=list)
    active_symbols: list[str] = field(default_factory=list)
    dominant_family_ids: list[str] = field(default_factory=list)
    turning_point: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class GraphStagePayload:
    event_id: str
    status: str
    shell: dict[str, Any] = field(default_factory=dict)
    event_graph: dict[str, Any] = field(default_factory=dict)
    nodes: list[WorkbenchNode] = field(default_factory=list)
    edges: list[WorkbenchEdge] = field(default_factory=list)
    current_highlights: GraphStageHighlights = field(default_factory=GraphStageHighlights)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["nodes"] = [node.to_dict() for node in self.nodes]
        payload["edges"] = [edge.to_dict() for edge in self.edges]
        payload["current_highlights"] = self.current_highlights.to_dict()
        return payload


@dataclass(frozen=True, slots=True)
class TradeCard:
    card_id: str
    participant_id: str
    participant_family: str
    action_type: str
    next_state: str
    polarity: str
    symbols: list[str] = field(default_factory=list)
    window: str = ""
    day_index: int = 0
    trade_date: str = ""
    expected_impact: str = ""
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

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class TradePulsePayload:
    event_id: str
    status: str
    round_id: str = ""
    window: str = ""
    day_index: int = 0
    trade_date: str = ""
    is_incremental_generated: bool = False
    market_state: str = ""
    dominant_scenario: str = ""
    actions_count: int = 0
    buy_clone_count: int = 0
    sell_clone_count: int = 0
    new_entry_clone_count: int = 0
    exit_clone_count: int = 0
    highlighted_clone_ids: list[str] = field(default_factory=list)
    highlighted_symbols: list[str] = field(default_factory=list)
    trade_cards: list[TradeCard] = field(default_factory=list)
    market_pulse_summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["trade_cards"] = [card.to_dict() for card in self.trade_cards]
        return payload


@dataclass(frozen=True, slots=True)
class DecisionTracePayload:
    event_id: str
    status: str
    clone_id: str
    round_id: str = ""
    day_index: int = 0
    trade_date: str = ""
    is_incremental_generated: bool = False
    clone_profile: dict[str, Any] = field(default_factory=dict)
    current_state: dict[str, Any] = field(default_factory=dict)
    seen_signals: list[str] = field(default_factory=list)
    influenced_by: list[dict[str, Any]] = field(default_factory=list)
    influences: list[dict[str, Any]] = field(default_factory=list)
    decision_chain: list[dict[str, Any]] = field(default_factory=list)
    executed_action: dict[str, Any] = field(default_factory=dict)
    expected_impact: str = ""
    threshold_summary: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class MarketStateTransitionPayload:
    event_id: str
    status: str
    transition_id: str
    from_state: str = ""
    to_state: str = ""
    previous_round_id: str = ""
    current_round_id: str = ""
    day_index: int = 0
    trade_date: str = ""
    triggering_clones: list[str] = field(default_factory=list)
    triggering_edges: list[dict[str, Any]] = field(default_factory=list)
    triggering_signals: list[str] = field(default_factory=list)
    market_metrics: dict[str, Any] = field(default_factory=dict)
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class WorkbenchReportPayload:
    event_id: str
    status: str
    replay_summary: dict[str, Any] = field(default_factory=dict)
    report: dict[str, Any] = field(default_factory=dict)
    validation: dict[str, Any] = field(default_factory=dict)
    scoreboards: dict[str, Any] = field(default_factory=dict)
    failure_taxonomy: list[dict[str, Any]] = field(default_factory=list)
    provenance: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class WorkbenchAskResponse:
    event_id: str
    status: str
    ask_type: str
    answer: str
    evidence_refs: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

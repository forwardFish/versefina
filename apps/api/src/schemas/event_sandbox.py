from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from schemas.influence_graph import ParticipantInfluenceEdge


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
    summary: str

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

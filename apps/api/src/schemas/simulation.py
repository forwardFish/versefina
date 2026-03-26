from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


SIMULATION_ACTION_PROTOCOL = (
    "IGNORE",
    "WATCH",
    "VALIDATE",
    "BROADCAST_BULL",
    "BROADCAST_BEAR",
    "LEAD",
    "FOLLOW",
    "EXIT",
)

SIMULATION_ACTION_DISPLAY_TYPES = {
    "IGNORE": "ignore",
    "WATCH": "risk_watch",
    "VALIDATE": "stabilize",
    "BROADCAST_BULL": "broadcast_bull",
    "BROADCAST_BEAR": "broadcast_bear",
    "LEAD": "first_move",
    "FOLLOW": "follow_on",
    "EXIT": "exit",
}

SIMULATION_ACTION_STATE_TRANSITIONS = {
    "IGNORE": ("ready", "watching"),
    "WATCH": ("ready", "watching"),
    "VALIDATE": ("watching", "validated"),
    "BROADCAST_BULL": ("validated", "broadcasting"),
    "BROADCAST_BEAR": ("validated", "broadcasting"),
    "LEAD": ("ready", "leading"),
    "FOLLOW": ("watching", "following"),
    "EXIT": ("broadcasting", "exited"),
}


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
        target_required=action_name not in {"IGNORE", "EXIT"},
        description=f"{action_name} is part of the P0 action vocabulary for roadmap_1_7.",
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
    role: str
    stance: str
    authority_weight: float
    confidence: float
    state: str = "ready"
    planned_allocation: float = 0.0
    trigger_signals: list[str] = field(default_factory=list)
    invalidation_signals: list[str] = field(default_factory=list)
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

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SimulationRoundResult:
    round_id: str
    order: int
    focus: str
    objective: str
    status: str
    participant_updates: list[SimulationParticipantUpdate] = field(default_factory=list)
    participant_states: list[dict[str, Any]] = field(default_factory=list)
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
    watchpoints: list[str] = field(default_factory=list)
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

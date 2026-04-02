from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


PARTICIPANT_FAMILIES = (
    "retail_fast_money",
    "institution_confirmation",
    "industry_research",
    "policy_research",
    "quant_risk_budget",
    "risk_control",
    "media_sentiment",
    "supply_chain_channel",
)

PARTICIPANT_STANCES = (
    "bullish",
    "constructive",
    "neutral",
    "watch",
    "skeptical",
    "bearish",
    "insufficient_evidence",
)

PARTICIPANT_TIME_HORIZONS = ("intraday", "t1", "t3", "t5_plus")
PARTICIPANT_INITIAL_STATES = ("ready", "watching", "validated", "broadcasting", "leading", "following", "exited")


@dataclass(frozen=True, slots=True)
class ParticipantOutput:
    participant_id: str
    participant_family: str
    style_variant: str
    stance: str
    confidence: float
    time_horizon: str
    expected_impact: str
    evidence: list[str] = field(default_factory=list)
    trigger_conditions: list[str] = field(default_factory=list)
    invalidation_conditions: list[str] = field(default_factory=list)
    first_movers: list[str] = field(default_factory=list)
    secondary_movers: list[str] = field(default_factory=list)
    dissent_points: list[str] = field(default_factory=list)
    initial_state: str = "ready"
    allowed_actions: list[str] = field(default_factory=list)
    authority_weight: float | None = None
    risk_budget_profile: str | None = None
    clone_index: int = 0
    influence_weight: float = 0.0
    capital_bucket: str = ""
    capital_base: float = 0.0
    cash_available: float = 0.0
    current_positions: dict[str, float] = field(default_factory=dict)
    max_event_exposure: float = 0.0
    reaction_latency: int = 0
    entry_threshold: float = 0.0
    add_threshold: float = 0.0
    reduce_threshold: float = 0.0
    exit_threshold: float = 0.0
    preferred_execution_windows: list[str] = field(default_factory=list)
    avoid_execution_windows: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

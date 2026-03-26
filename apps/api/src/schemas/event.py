from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


EVENT_LIFECYCLE_STATUSES = ("raw", "structured", "prepared", "simulated", "reviewed")


@dataclass(frozen=True, slots=True)
class EventRecord:
    event_id: str
    title: str
    body: str
    source: str
    event_time: str
    status: str = "raw"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class EventStructure:
    event_id: str
    event_type: str
    entities: list[str] = field(default_factory=list)
    commodities: list[str] = field(default_factory=list)
    chain_links: list[dict[str, str]] = field(default_factory=list)
    sectors: list[str] = field(default_factory=list)
    affected_symbols: list[str] = field(default_factory=list)
    target_symbols: list[str] = field(default_factory=list)
    causal_chain: list[str] = field(default_factory=list)
    monitor_signals: list[str] = field(default_factory=list)
    trigger_signals: list[str] = field(default_factory=list)
    invalidation_conditions: list[str] = field(default_factory=list)
    confidence: float = 0.0
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ThemeMappingResult:
    event_id: str
    commodity: str
    chain_stage: str
    sector: str
    symbols: list[str] = field(default_factory=list)
    style_tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class EventCasebookEntry:
    event_id: str
    record: dict[str, Any]
    structure: dict[str, Any]
    mapping: dict[str, Any]
    status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class EventCardReadModel:
    event_id: str
    status: str
    event_summary: str
    participant_summary: list[str] = field(default_factory=list)
    graph_summary: dict[str, Any] = field(default_factory=dict)
    scenarios: list[dict[str, Any]] = field(default_factory=list)
    simulation_summary: dict[str, Any] = field(default_factory=dict)
    watchpoints: list[str] = field(default_factory=list)
    invalidation_conditions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


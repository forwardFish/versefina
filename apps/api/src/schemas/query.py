from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class AgentSnapshot:
    agent_id: str
    world_id: str
    status: str
    summary: str


@dataclass(frozen=True, slots=True)
class TradeLogView:
    agent_id: str
    items: list[dict[str, str]] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class EquityCurve:
    agent_id: str
    points: list[dict[str, str]] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class RankingBoard:
    as_of_day: str
    items: list[dict[str, str]] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class PanoramaView:
    world_id: str
    cards: list[dict[str, str]] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class WorldSnapshot:
    world_id: str
    trading_day: str
    headline: str

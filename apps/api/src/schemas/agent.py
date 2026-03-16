from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class Position:
    symbol: str
    qty: int
    avg_cost: float


@dataclass(frozen=True, slots=True)
class AgentSnapshot:
    agent_id: str
    owner_id: str
    world_id: str
    status: str
    equity: float
    cash: float
    drawdown: float
    statement_id: str | None = None
    public_url: str | None = None
    profile_path: str | None = None
    source_runtime: str = "native"
    tags: list[str] = field(default_factory=list)
    positions: list[Position] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class TradingAgentProfile:
    statement_id: str
    market: str
    styleTags: list[str] = field(default_factory=list)
    preferredUniverse: list[dict[str, str]] = field(default_factory=list)
    riskControls: dict[str, float | int] = field(default_factory=dict)
    cadence: dict[str, int] = field(default_factory=dict)
    costModel: dict[str, float] = field(default_factory=dict)
    decisionPolicy: dict[str, Any] = field(default_factory=dict)
    sourceRuntime: str = "native"
    profileVersion: str = "v1"
    generatedAt: str = ""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class Position:
    symbol: str
    qty: int
    avg_cost: float


@dataclass(frozen=True, slots=True)
class AgentSnapshot:
    agent_id: str
    status: str
    equity: float
    cash: float
    drawdown: float
    tags: list[str] = field(default_factory=list)
    positions: list[Position] = field(default_factory=list)

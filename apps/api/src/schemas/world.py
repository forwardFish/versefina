from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WorldSnapshot:
    world_id: str
    market: str
    trading_day: str
    next_trading_day: str | None
    total_agents: int
    market_status: str
    source: str = "fallback"
    available_trading_days: list[str] | None = None

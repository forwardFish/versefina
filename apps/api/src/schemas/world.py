from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WorldSnapshot:
    trading_day: str
    total_agents: int
    market_status: str

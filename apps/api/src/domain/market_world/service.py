from __future__ import annotations

from dataclasses import dataclass

from schemas.world import WorldSnapshot


@dataclass(slots=True)
class MarketWorldService:
    default_world_id: str

    def panorama(self) -> WorldSnapshot:
        return WorldSnapshot(trading_day="2026-03-12", total_agents=1, market_status="open")

    def snapshot(self, world_id: str) -> WorldSnapshot:
        return WorldSnapshot(trading_day="2026-03-12", total_agents=1, market_status="open")

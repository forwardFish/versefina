from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TradeLog:
    symbol: str
    qty: int
    avg_cost: float

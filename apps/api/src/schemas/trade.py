from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TradeLog:
    symbol: str
    qty: int
    avg_cost: float


@dataclass(frozen=True, slots=True)
class TradeRecord:
    statement_id: str
    traded_at: str
    symbol: str
    side: str
    qty: int
    price: float
    fee: float
    tax: float
    broker: str
    row_number: int

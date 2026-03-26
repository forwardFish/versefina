from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class StatementBehaviorFeatures:
    statement_id: str
    status: str
    trade_count: int
    source_trade_record_path: str
    holding_period: dict[str, Any] = field(default_factory=dict)
    add_reduce_pattern: dict[str, Any] = field(default_factory=dict)
    momentum_preference: dict[str, Any] = field(default_factory=dict)
    drawdown_tolerance: dict[str, Any] = field(default_factory=dict)
    feature_vector: dict[str, float] = field(default_factory=dict)
    low_confidence: bool = False
    confidence_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

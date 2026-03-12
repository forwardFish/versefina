from __future__ import annotations

from dataclasses import dataclass

from schemas.query import RankingBoard


@dataclass(slots=True)
class RankingProjection:
    def list_rankings(self) -> RankingBoard:
        return RankingBoard(
            as_of_day="2026-03-12",
            items=[
                {"agent_id": "alpha-01", "return": "+8.2%"},
                {"agent_id": "value-02", "return": "+6.4%"},
            ],
        )

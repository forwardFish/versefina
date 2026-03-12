from __future__ import annotations

from dataclasses import dataclass

from schemas.agent import AgentSnapshot


@dataclass(slots=True)
class AgentSnapshotProjection:
    def present(self, snapshot: AgentSnapshot) -> AgentSnapshot:
        return snapshot

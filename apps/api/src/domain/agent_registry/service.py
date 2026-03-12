from __future__ import annotations

from dataclasses import dataclass

from schemas.common import AcceptedResponse
from schemas.command import AgentRegisterRequest, HeartbeatRequest
from schemas.agent import AgentSnapshot, Position


@dataclass(slots=True)
class AgentRegistryService:
    default_world_id: str

    def register(self, payload: AgentRegisterRequest) -> AcceptedResponse:
        return AcceptedResponse(status="accepted", task_id=f"register::{payload.agent_id}")

    def heartbeat(self, agent_id: str, payload: HeartbeatRequest) -> AcceptedResponse:
        return AcceptedResponse(status="accepted", task_id=f"heartbeat::{agent_id}::{payload.heartbeat_at}")

    def snapshot(self, agent_id: str) -> AgentSnapshot:
        return AgentSnapshot(
            agent_id=agent_id,
            status="active",
            equity=105000.0,
            cash=50000.0,
            drawdown=0.05,
            tags=["trend", "swing"],
            positions=[
                Position(symbol="600519.SH", qty=100, avg_cost=1680.0),
                Position(symbol="000001.SZ", qty=300, avg_cost=12.45),
                Position(symbol="AAPL", qty=25, avg_cost=182.3),
            ],
        )

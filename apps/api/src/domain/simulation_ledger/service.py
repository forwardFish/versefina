from __future__ import annotations

from dataclasses import dataclass

from schemas.common import AcceptedResponse
from schemas.command import SubmitActionRequest
from schemas.query import EquityCurve, TradeLogView


@dataclass(slots=True)
class SimulationLedgerService:
    def submit_actions(self, payload: SubmitActionRequest) -> AcceptedResponse:
        return AcceptedResponse(status="accepted", task_id=f"actions::{payload.agent_id}")

    def trades(self, agent_id: str) -> TradeLogView:
        return TradeLogView(agent_id=agent_id, items=[{"symbol": "600519.SH", "side": "BUY", "qty": "100"}])

    def equity(self, agent_id: str) -> EquityCurve:
        return EquityCurve(agent_id=agent_id, points=[{"trading_day": "2026-03-12", "equity": "1000000"}])

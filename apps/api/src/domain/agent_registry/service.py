from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
import json
from pathlib import Path

from schemas.common import AcceptedResponse
from schemas.command import AgentCreateRequest, AgentCreateResponse, AgentRegisterRequest, HeartbeatRequest
from schemas.agent import AgentSnapshot, Position


@dataclass(slots=True)
class AgentRegistryService:
    default_world_id: str
    registry_root: Path
    public_base_url: str

    def __post_init__(self) -> None:
        self.registry_root.mkdir(parents=True, exist_ok=True)

    def register(self, payload: AgentRegisterRequest) -> AcceptedResponse:
        return AcceptedResponse(status="accepted", task_id=f"register::{payload.agent_id}")

    def heartbeat(self, agent_id: str, payload: HeartbeatRequest) -> AcceptedResponse:
        existing = self.get_agent(agent_id)
        if existing is not None:
            existing["last_heartbeat_at"] = payload.heartbeat_at
            existing["status"] = payload.status.lower()
            self._write_agent(agent_id, existing)
        return AcceptedResponse(status="accepted", task_id=f"heartbeat::{agent_id}::{payload.heartbeat_at}")

    def create_agent(
        self,
        payload: AgentCreateRequest,
        *,
        profile: dict,
        profile_path: str,
        public_base_url: str | None = None,
    ) -> AgentCreateResponse:
        agent_id = payload.agent_id or f"agt_{payload.statement_id.replace('-', '_')}"
        created_at = datetime.now().isoformat()
        world_id = payload.world_id or self.default_world_id
        base_url = (public_base_url or self.public_base_url).rstrip("/")
        public_url = f"{base_url}/api/v1/agents/{agent_id}"
        tags = list(profile.get("styleTags") or [])
        risk_controls = dict(profile.get("riskControls") or {})
        record = {
            "agent_id": agent_id,
            "owner_id": payload.owner_id,
            "statement_id": payload.statement_id,
            "world_id": world_id,
            "status": "active",
            "init_cash": float(payload.init_cash),
            "cash": float(payload.init_cash),
            "equity": float(payload.init_cash),
            "drawdown": 0.0,
            "public_url": public_url,
            "profile_path": profile_path,
            "source_runtime": payload.source_runtime,
            "tags": tags,
            "risk_controls": risk_controls,
            "positions": [],
            "created_at": created_at,
            "last_heartbeat_at": None,
        }
        self._write_agent(agent_id, record)
        return AgentCreateResponse(
            agent_id=agent_id,
            owner_id=payload.owner_id,
            statement_id=payload.statement_id,
            world_id=world_id,
            status="active",
            init_cash=float(payload.init_cash),
            public_url=public_url,
            profile_path=profile_path,
            source_runtime=payload.source_runtime,
            created_at=created_at,
        )

    def get_agent(self, agent_id: str) -> dict | None:
        path = self.registry_root / f"{agent_id}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def snapshot(self, agent_id: str) -> AgentSnapshot:
        record = self.get_agent(agent_id)
        if record is not None:
            return AgentSnapshot(
                agent_id=agent_id,
                owner_id=str(record["owner_id"]),
                world_id=str(record["world_id"]),
                status=str(record["status"]),
                equity=float(record["equity"]),
                cash=float(record["cash"]),
                drawdown=float(record["drawdown"]),
                statement_id=str(record.get("statement_id") or "") or None,
                public_url=record.get("public_url"),
                profile_path=record.get("profile_path"),
                source_runtime=str(record.get("source_runtime") or "native"),
                tags=list(record.get("tags") or []),
                positions=[
                    Position(
                        symbol=str(position["symbol"]),
                        qty=int(position["qty"]),
                        avg_cost=float(position["avg_cost"]),
                    )
                    for position in (record.get("positions") or [])
                ],
            )
        return AgentSnapshot(
            agent_id=agent_id,
            owner_id="demo-user",
            world_id=self.default_world_id,
            status="active",
            equity=105000.00,
            cash=50000.00,
            drawdown=0.05,
            public_url=f"{self.public_base_url.rstrip('/')}/api/v1/agents/{agent_id}",
            tags=["趋势", "短线"],
            positions=[
                Position(symbol="600519.SH", qty=100, avg_cost=1680.0),
                Position(symbol="000001.SZ", qty=300, avg_cost=12.45),
            ],
        )

    def _write_agent(self, agent_id: str, payload: dict) -> None:
        path = self.registry_root / f"{agent_id}.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

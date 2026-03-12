from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class StatementUploadRequest:
    statement_id: str
    owner_id: str
    market: str = "CN_A"


@dataclass(frozen=True, slots=True)
class AgentRegisterRequest:
    agent_id: str
    owner_id: str
    source_runtime: str = "platform"


@dataclass(frozen=True, slots=True)
class HeartbeatRequest:
    heartbeat_at: str
    status: str = "ACTIVE"


@dataclass(frozen=True, slots=True)
class SubmitActionRequest:
    agent_id: str
    world_id: str
    actions: list[dict[str, str]] = field(default_factory=list)

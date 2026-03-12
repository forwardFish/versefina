from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class OpenClawRegisterRequest:
    openclaw_agent_id: str
    agent_id: str


@dataclass(frozen=True, slots=True)
class OpenClawHeartbeatRequest:
    openclaw_agent_id: str
    heartbeat_at: str


@dataclass(frozen=True, slots=True)
class OpenClawSubmitActionRequest:
    openclaw_agent_id: str
    world_id: str
    actions: list[dict[str, str]] = field(default_factory=list)

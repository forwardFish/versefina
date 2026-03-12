from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class AcceptedResponse:
    status: str
    task_id: str


@dataclass(frozen=True, slots=True)
class HealthResponse:
    service: str
    status: str
    routers: list[str] = field(default_factory=list)

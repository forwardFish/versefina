from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True, slots=True)
class AcceptanceBoundary:
    priority: str
    label: str
    objective: str
    sprints: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class MigrationMapping:
    legacy_sprint: str
    target_lane: str
    target_sprints: list[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class AcceptanceArtifactRef:
    sprint: str
    story_id: str
    path: str
    summary: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class AcceptanceHandoffSnapshot:
    path: str
    sprint: str
    story: str
    status: str
    next_action: str
    recovery_command: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RoadmapAcceptancePack:
    roadmap_id: str
    status: str
    headline: str
    story_execution_rule: str
    p0_boundaries: list[AcceptanceBoundary] = field(default_factory=list)
    p1_boundaries: list[AcceptanceBoundary] = field(default_factory=list)
    migration_map: list[MigrationMapping] = field(default_factory=list)
    continuity_files: list[str] = field(default_factory=list)
    delivery_artifacts: list[AcceptanceArtifactRef] = field(default_factory=list)
    current_handoff: AcceptanceHandoffSnapshot | None = None
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

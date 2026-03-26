from __future__ import annotations

from dataclasses import asdict
import json
import re
from pathlib import Path

from schemas.e7_005 import (
    AcceptanceArtifactRef,
    AcceptanceBoundary,
    AcceptanceHandoffSnapshot,
    MigrationMapping,
    RoadmapAcceptancePack,
)


class AcceptancePackError(Exception):
    def __init__(self, *, code: str, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class AcceptancePackService:
    ROADMAP_ID = "roadmap_1_6"

    def __init__(self, *, repo_root: Path, acceptance_root: Path) -> None:
        self.repo_root = repo_root
        self.acceptance_root = acceptance_root
        self.acceptance_root.mkdir(parents=True, exist_ok=True)

    def build_acceptance_pack(self) -> RoadmapAcceptancePack:
        continuity_files = self._require_paths(
            [
                self.repo_root / "NOW.md",
                self.repo_root / "STATE.md",
                self.repo_root / "DECISIONS.md",
                self.repo_root / "tasks" / "sprint_overview_1_6_event_participant_first.md",
                self.repo_root / "docs" / "handoff" / "current_handoff.md",
            ]
        )
        delivery_artifacts = self._collect_delivery_artifacts()
        handoff_snapshot = self._load_handoff_snapshot(self.repo_root / "docs" / "handoff" / "current_handoff.md")
        pack = RoadmapAcceptancePack(
            roadmap_id=self.ROADMAP_ID,
            status="ready",
            headline="Roadmap 1.6 MVP acceptance pack and migration handoff",
            story_execution_rule="Continue only from the current_handoff safe point and execute roadmap_1_6 stories in order; do not reopen legacy sprint_1-sprint_9 as the authoritative lane.",
            p0_boundaries=[
                AcceptanceBoundary(
                    priority="P0",
                    label="Event-participant-first MVP lane",
                    objective="Keep Sprint 1-5 as the must-run product lane for event ingestion, participant prep, belief/scenario reasoning, simulation runtime, and review APIs.",
                    sprints=[f"Sprint {index}" for index in range(1, 6)],
                )
            ],
            p1_boundaries=[
                AcceptanceBoundary(
                    priority="P1",
                    label="Style and mirror calibration extension",
                    objective="Treat Sprint 6-7 as enhancement layers that turn statements into style assets and mirror-agent calibration packs after the P0 lane is stable.",
                    sprints=["Sprint 6", "Sprint 7"],
                )
            ],
            migration_map=self._build_migration_map(),
            continuity_files=[str(path) for path in continuity_files[:3]],
            delivery_artifacts=delivery_artifacts,
            current_handoff=handoff_snapshot,
            notes=[
                "The acceptance pack distinguishes P0 versus P1 so the team can preserve the event-participant-first main line while keeping statement style calibration as an enhancement lane.",
                "The migration map explains how legacy Sprint 1-9 expectations collapse into roadmap_1_6 without losing the new authoritative execution order.",
                "Use NOW.md, STATE.md, DECISIONS.md, and current_handoff.md together as the fresh-chat recovery set.",
            ],
        )
        self._persist(pack)
        return pack

    def load_acceptance_pack(self) -> RoadmapAcceptancePack | None:
        target_path = self.acceptance_root / f"{self.ROADMAP_ID}.json"
        if not target_path.exists():
            return None
        payload = json.loads(target_path.read_text(encoding="utf-8"))
        payload["p0_boundaries"] = [AcceptanceBoundary(**item) for item in payload.get("p0_boundaries", [])]
        payload["p1_boundaries"] = [AcceptanceBoundary(**item) for item in payload.get("p1_boundaries", [])]
        payload["migration_map"] = [MigrationMapping(**item) for item in payload.get("migration_map", [])]
        payload["delivery_artifacts"] = [AcceptanceArtifactRef(**item) for item in payload.get("delivery_artifacts", [])]
        handoff_payload = payload.get("current_handoff")
        payload["current_handoff"] = AcceptanceHandoffSnapshot(**handoff_payload) if handoff_payload else None
        return RoadmapAcceptancePack(**payload)

    def _require_paths(self, paths: list[Path]) -> list[Path]:
        missing = [str(path) for path in paths if not path.exists()]
        if missing:
            raise AcceptancePackError(
                code="ROADMAP_SUPPORT_FILE_MISSING",
                message=f"Acceptance pack requires support files before build: {', '.join(missing)}",
                status_code=404,
            )
        return paths

    def _collect_delivery_artifacts(self) -> list[AcceptanceArtifactRef]:
        requirements_root = self.repo_root / "docs" / "requirements"
        if not requirements_root.exists():
            raise AcceptancePackError(
                code="ROADMAP_DELIVERY_DOCS_MISSING",
                message="Roadmap delivery docs root is missing.",
                status_code=404,
            )

        artifacts: list[AcceptanceArtifactRef] = []
        covered_sprints: set[int] = set()
        pattern = re.compile(r"^e(?P<sprint>\d+)_(?P<story>\d{3})_delivery$", re.IGNORECASE)
        for path in sorted(requirements_root.glob("e*_delivery.md")):
            match = pattern.match(path.stem)
            if match is None:
                continue
            sprint_number = int(match.group("sprint"))
            story_number = match.group("story")
            covered_sprints.add(sprint_number)
            artifacts.append(
                AcceptanceArtifactRef(
                    sprint=f"Sprint {sprint_number}",
                    story_id=f"E{sprint_number}-{story_number}",
                    path=str(path),
                    summary=self._summarize_delivery_doc(path),
                )
            )

        missing_sprints = [f"Sprint {index}" for index in range(1, 8) if index not in covered_sprints]
        if missing_sprints:
            raise AcceptancePackError(
                code="ROADMAP_DELIVERY_DOCS_MISSING",
                message=f"Acceptance pack needs delivery evidence for every roadmap sprint. Missing: {', '.join(missing_sprints)}",
                status_code=404,
            )
        return artifacts

    def _summarize_delivery_doc(self, path: Path) -> str:
        for line in path.read_text(encoding="utf-8").splitlines():
            candidate = line.strip()
            if not candidate or candidate.startswith("#"):
                continue
            if candidate.startswith("- "):
                return candidate[2:]
            return candidate
        return "Delivery evidence recorded."

    def _load_handoff_snapshot(self, path: Path) -> AcceptanceHandoffSnapshot:
        text = path.read_text(encoding="utf-8")
        metadata: dict[str, str] = {}
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line.startswith("- ") or ":" not in line:
                continue
            key, value = line[2:].split(":", 1)
            metadata[key.strip().lower().replace(" ", "_")] = value.strip()
        return AcceptanceHandoffSnapshot(
            path=str(path),
            sprint=metadata.get("sprint", ""),
            story=metadata.get("story", ""),
            status=metadata.get("status", ""),
            next_action=self._extract_section(text, "## Next Action"),
            recovery_command=self._extract_section(text, "## Recovery Command"),
        )

    def _extract_section(self, text: str, heading: str) -> str:
        lines = text.splitlines()
        for index, line in enumerate(lines):
            if line.strip() != heading:
                continue
            collected: list[str] = []
            for candidate in lines[index + 1 :]:
                stripped = candidate.strip()
                if stripped.startswith("## "):
                    break
                if stripped:
                    collected.append(stripped)
            return " ".join(collected)
        return ""

    def _build_migration_map(self) -> list[MigrationMapping]:
        return [
            MigrationMapping(
                legacy_sprint="Sprint 1",
                target_lane="roadmap_1_6 event lane foundation",
                target_sprints=["Sprint 1"],
                notes="Freeze event whitelist, event record structure, event parsing, theme mapping, and casebook foundation here.",
            ),
            MigrationMapping(
                legacy_sprint="Sprint 2",
                target_lane="event participant preparation",
                target_sprints=["Sprint 2"],
                notes="Carry participant preparation and prepare orchestrator into the new event-participant-first chain.",
            ),
            MigrationMapping(
                legacy_sprint="Sprint 3",
                target_lane="belief graph and scenario reasoning",
                target_sprints=["Sprint 3"],
                notes="Move belief graph, scenario engine, watchpoints, and event card read model into the authoritative lane.",
            ),
            MigrationMapping(
                legacy_sprint="Sprint 4",
                target_lane="simulation runtime",
                target_sprints=["Sprint 4"],
                notes="Keep simulation runtime, timeline, and action log in the new main execution path.",
            ),
            MigrationMapping(
                legacy_sprint="Sprint 5",
                target_lane="review and retrieval APIs",
                target_sprints=["Sprint 5"],
                notes="Map review report, T+1/T+3 outcomes, reliability, and why retrieval into the acceptance-ready API layer.",
            ),
            MigrationMapping(
                legacy_sprint="Sprint 6",
                target_lane="style asset extension",
                target_sprints=["Sprint 6"],
                notes="Statement-to-style assets becomes the first enhancement lane after the P0 roadmap is stable.",
            ),
            MigrationMapping(
                legacy_sprint="Sprint 7",
                target_lane="mirror agent extension",
                target_sprints=["Sprint 7"],
                notes="Mirror agent and distribution calibration remain enhancement work but still belong to roadmap_1_6 delivery evidence.",
            ),
            MigrationMapping(
                legacy_sprint="Sprint 8",
                target_lane="post-roadmap extension planning",
                target_sprints=["Sprint 7"],
                notes="Legacy Sprint 8 expectations should be decomposed into future stories after roadmap_1_6 closeout instead of reopening the old lane.",
            ),
            MigrationMapping(
                legacy_sprint="Sprint 9",
                target_lane="post-roadmap release planning",
                target_sprints=["Sprint 7"],
                notes="Legacy Sprint 9 becomes downstream release planning and handoff work after the new acceptance pack is published.",
            ),
        ]

    def _persist(self, pack: RoadmapAcceptancePack) -> None:
        target_path = self.acceptance_root / f"{self.ROADMAP_ID}.json"
        target_path.write_text(json.dumps(asdict(pack), ensure_ascii=False, indent=2), encoding="utf-8")

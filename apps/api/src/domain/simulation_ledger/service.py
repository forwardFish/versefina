from __future__ import annotations

import json
from pathlib import Path

from schemas.query import EquityCurve, TradeLogView
from schemas.simulation import SimulationRoundResult
from schemas.simulation_ledger import (
    SimulationActionLogEntry,
    SimulationActionLogView,
    SimulationStateSnapshot,
    SimulationStateSnapshotView,
)


class SimulationLedgerService:
    def __init__(self, runtime_root: Path) -> None:
        self.runtime_root = runtime_root
        self.runs_root = runtime_root / "runs"
        self.actions_root = runtime_root / "actions"
        self.snapshots_root = runtime_root / "snapshots"
        self.runs_root.mkdir(parents=True, exist_ok=True)
        self.actions_root.mkdir(parents=True, exist_ok=True)
        self.snapshots_root.mkdir(parents=True, exist_ok=True)

    def persist_round_results(
        self,
        *,
        event_id: str,
        run_id: str,
        round_results: list[SimulationRoundResult],
    ) -> tuple[Path, list[Path]]:
        action_log_path = self.actions_root / f"{run_id}.jsonl"
        snapshot_paths: list[Path] = []

        with action_log_path.open("w", encoding="utf-8") as handle:
            for round_result in round_results:
                for update in round_result.participant_updates:
                    entry = SimulationActionLogEntry(
                        event_id=event_id,
                        run_id=run_id,
                        round_id=round_result.round_id,
                        order=round_result.order,
                        participant_id=update.participant_id,
                        actor_id=update.actor_id or update.participant_id,
                        target_id=update.target_id,
                        action_name=update.action_name or update.action_type.upper(),
                        action_type=update.action_type,
                        confidence=update.confidence,
                        reason_code=update.reason_code or (update.reason_codes[0] if update.reason_codes else ""),
                        reason_codes=list(update.reason_codes),
                        state_before=update.previous_state,
                        state_after=update.next_state,
                    )
                    handle.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")

                snapshot = SimulationStateSnapshot(
                    event_id=event_id,
                    run_id=run_id,
                    round_id=round_result.round_id,
                    order=round_result.order,
                    participant_states=list(round_result.participant_states),
                )
                snapshot_path = self.snapshots_root / f"{run_id}-{round_result.round_id}.json"
                snapshot_path.write_text(json.dumps(snapshot.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
                snapshot_paths.append(snapshot_path)

        return action_log_path, snapshot_paths

    def load_action_log(self, event_id: str, run_id: str | None = None) -> SimulationActionLogView:
        resolved_run_id = run_id or self._latest_run_id_for_event(event_id)
        if not resolved_run_id:
            return SimulationActionLogView(event_id=event_id, status="simulation_missing")

        action_log_path = self.actions_root / f"{resolved_run_id}.jsonl"
        if not action_log_path.exists():
            return SimulationActionLogView(event_id=event_id, run_id=resolved_run_id, status="action_log_missing")

        entries = [
            SimulationActionLogEntry(**json.loads(line))
            for line in action_log_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        return SimulationActionLogView(
            event_id=event_id,
            run_id=resolved_run_id,
            status="ready",
            path=str(action_log_path),
            entries=entries,
        )

    def load_state_snapshots(self, event_id: str, run_id: str | None = None) -> SimulationStateSnapshotView:
        resolved_run_id = run_id or self._latest_run_id_for_event(event_id)
        if not resolved_run_id:
            return SimulationStateSnapshotView(event_id=event_id, status="simulation_missing")

        snapshot_paths = sorted(self.snapshots_root.glob(f"{resolved_run_id}-round-*.json"))
        if not snapshot_paths:
            return SimulationStateSnapshotView(event_id=event_id, run_id=resolved_run_id, status="snapshot_missing")

        snapshots = [
            SimulationStateSnapshot(**json.loads(path.read_text(encoding="utf-8")))
            for path in snapshot_paths
        ]
        return SimulationStateSnapshotView(
            event_id=event_id,
            run_id=resolved_run_id,
            status="ready",
            snapshots=snapshots,
            paths=[str(path) for path in snapshot_paths],
        )

    def trades(self, agent_id: str) -> TradeLogView:
        return TradeLogView(agent_id=agent_id, items=[])

    def equity(self, agent_id: str) -> EquityCurve:
        return EquityCurve(agent_id=agent_id, points=[])

    def _latest_run_id_for_event(self, event_id: str) -> str:
        candidates = sorted(self.runs_root.glob(f"{event_id}-run-*.json"))
        if not candidates:
            return ""
        return candidates[-1].stem

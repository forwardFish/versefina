from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from domain.belief_graph.service import BeliefGraphError, BeliefGraphService
from domain.event_casebook.service import EventCasebookService
from domain.simulation_ledger.service import SimulationLedgerService
from domain.scenario_engine.service import ScenarioEngineError, ScenarioEngineService
from domain.event_simulation.timeline import build_simulation_timeline
from schemas.simulation import (
    SimulationExecutionResult,
    SimulationParticipantState,
    SimulationPrepareResult,
    SimulationRoundPlan,
    SimulationRun,
)
from workflows.event_simulation.graph import build_event_simulation_graph, execute_event_simulation_graph


class EventSimulationError(Exception):
    def __init__(self, *, code: str, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class EventSimulationService:
    def __init__(
        self,
        *,
        runtime_root: Path,
        casebook_service: EventCasebookService,
        belief_graph: BeliefGraphService,
        scenario_engine: ScenarioEngineService,
        simulation_ledger: SimulationLedgerService | None = None,
    ) -> None:
        self.runtime_root = runtime_root
        self.casebook_service = casebook_service
        self.belief_graph = belief_graph
        self.scenario_engine = scenario_engine
        self.simulation_ledger = simulation_ledger
        self.runs_root = runtime_root / "runs"
        self.actions_root = runtime_root / "actions"
        self.snapshots_root = runtime_root / "snapshots"
        self.runs_root.mkdir(parents=True, exist_ok=True)
        self.actions_root.mkdir(parents=True, exist_ok=True)
        self.snapshots_root.mkdir(parents=True, exist_ok=True)

    def prepare_run(self, event_id: str) -> SimulationPrepareResult:
        casebook = self.casebook_service.load_casebook(event_id)
        if casebook is None:
            raise EventSimulationError(
                code="EVENT_NOT_FOUND",
                message="Event casebook not found.",
                status_code=404,
            )

        try:
            graph_snapshot = self.belief_graph.build_snapshot(event_id)
        except BeliefGraphError as exc:
            raise EventSimulationError(code=exc.code, message=exc.message, status_code=exc.status_code) from exc

        try:
            scenario_result = self.scenario_engine.build_scenarios(event_id)
        except ScenarioEngineError as exc:
            raise EventSimulationError(code=exc.code, message=exc.message, status_code=exc.status_code) from exc

        dominant_scenario = str(scenario_result.dominant_scenario or "").strip()
        if not dominant_scenario:
            raise EventSimulationError(
                code="DOMINANT_SCENARIO_MISSING",
                message="Simulation prepare requires a dominant scenario before execution.",
                status_code=409,
            )

        dominant_case = next(
            (scenario for scenario in scenario_result.scenarios if scenario.scenario_id == dominant_scenario),
            None,
        )
        if dominant_case is None:
            raise EventSimulationError(
                code="SCENARIO_CASE_MISSING",
                message="The dominant scenario could not be resolved from the scenario pack.",
                status_code=409,
            )

        participant_states = self._build_participant_states(
            graph_snapshot=graph_snapshot,
            dominant_scenario=dominant_scenario,
            dominant_case=dominant_case,
        )
        rounds = self._build_rounds(
            dominant_scenario=dominant_scenario,
            watchpoints=list(dominant_case.watchpoints),
            graph_status=scenario_result.graph_status,
        )
        run_id = self._next_run_id(event_id)
        simulation_run = SimulationRun(
            run_id=run_id,
            event_id=event_id,
            status="prepared",
            graph_status=scenario_result.graph_status,
            dominant_scenario=dominant_scenario,
            round_count=len(rounds),
            participant_states=participant_states,
            rounds=rounds,
            watchpoints=list(dominant_case.watchpoints),
            created_at=self._now_iso(),
        )
        self._persist_run(simulation_run)
        runner_payload = {
            "run_id": run_id,
            "event_id": event_id,
            "dominant_scenario": dominant_scenario,
            "graph_status": scenario_result.graph_status,
            "focus_symbols": list(casebook.mapping.get("symbols") or []),
            "participant_states": [state.to_dict() for state in participant_states],
            "rounds": [round_plan.to_dict() for round_plan in rounds],
            "watchpoints": list(dominant_case.watchpoints),
            "invalidation_conditions": list(dominant_case.invalidation_conditions),
        }
        return SimulationPrepareResult(
            event_id=event_id,
            status="prepared",
            simulation_run=simulation_run.to_dict(),
            runner_payload=runner_payload,
        )

    def run_simulation(self, event_id: str) -> SimulationExecutionResult:
        prepared = self.prepare_run(event_id)
        runner_payload = prepared.runner_payload
        participant_states = [
            SimulationParticipantState(**item)
            for item in runner_payload.get("participant_states", [])
        ]
        rounds = [SimulationRoundPlan(**item) for item in runner_payload.get("rounds", [])]
        dominant_scenario = str(runner_payload.get("dominant_scenario") or "")
        graph_status = str(runner_payload.get("graph_status") or "")
        graph = build_event_simulation_graph(rounds=rounds, dominant_scenario=dominant_scenario)
        round_results, final_participant_states = execute_event_simulation_graph(
            rounds=rounds,
            participant_states=participant_states,
            dominant_scenario=dominant_scenario,
            graph_status=graph_status,
        )
        timeline = build_simulation_timeline(round_results)
        run_id = str(prepared.simulation_run.get("run_id") or "")
        if self.simulation_ledger is not None:
            action_log_path, state_snapshots = self.simulation_ledger.persist_round_results(
                event_id=event_id,
                run_id=run_id,
                round_results=round_results,
            )
        else:
            action_log_path = self._persist_action_log(
                run_id=run_id,
                round_results=round_results,
            )
            state_snapshots = self._persist_state_snapshots(
                run_id=run_id,
                round_results=round_results,
            )
        simulation_run_payload = dict(prepared.simulation_run)
        simulation_run_payload["status"] = "completed"
        simulation_run_payload["graph"] = graph
        simulation_run_payload["participant_states"] = [state.to_dict() for state in final_participant_states]
        simulation_run_payload["round_results"] = [round_result.to_dict() for round_result in round_results]
        simulation_run_payload["timeline"] = timeline.to_dict()
        simulation_run_payload["action_log_path"] = str(action_log_path)
        simulation_run_payload["state_snapshots"] = [str(path) for path in state_snapshots]
        simulation_run_payload["completed_at"] = self._now_iso()
        self._persist_run_payload(simulation_run_payload)
        return SimulationExecutionResult(
            event_id=event_id,
            status="completed",
            simulation_run=simulation_run_payload,
            round_results=[round_result.to_dict() for round_result in round_results],
            final_participant_states=[state.to_dict() for state in final_participant_states],
            timeline=timeline.to_dict(),
        )

    def load_latest_run(self, event_id: str) -> dict[str, Any] | None:
        candidates = sorted(self.runs_root.glob(f"{event_id}-run-*.json"))
        if not candidates:
            return None
        return json.loads(candidates[-1].read_text(encoding="utf-8"))

    def _build_participant_states(self, *, graph_snapshot, dominant_scenario: str, dominant_case) -> list[SimulationParticipantState]:
        first_movers = set(dominant_case.first_movers)
        followers = set(dominant_case.followers)
        participant_states: list[SimulationParticipantState] = []
        for node in graph_snapshot.nodes:
            role = "risk_watch"
            if node.participant_family in first_movers:
                role = "first_move"
            elif node.participant_family in followers:
                role = "follow_on"
            participant_states.append(
                SimulationParticipantState(
                    participant_id=node.participant_id,
                    participant_family=node.participant_family,
                    role=role,
                    stance=node.stance,
                    authority_weight=node.authority_weight,
                    confidence=node.confidence,
                    state="ready",
                    planned_allocation=self._allocation_for(role, node.authority_weight, node.confidence),
                    trigger_signals=list(graph_snapshot.consensus_signals[:3]),
                    invalidation_signals=list(graph_snapshot.divergence_signals[:3]),
                    reason_codes=[
                        f"scenario:{dominant_scenario}",
                        f"role:{role}",
                        f"stance:{node.stance}",
                    ],
                )
            )
        return participant_states

    def _build_rounds(self, *, dominant_scenario: str, watchpoints: list[str], graph_status: str) -> list[SimulationRoundPlan]:
        round_focus = {
            "base": [
                ("round-1", "Signal Setup", "Establish the opening posture from the dominant path."),
                ("round-2", "Confirmation", "Check whether followers reinforce the first move."),
                ("round-3", "Risk Check", "Stop the run if watchpoints fail to confirm."),
            ],
            "bull": [
                ("round-1", "Ignition", "Track the first movers that should react immediately."),
                ("round-2", "Expansion", "Measure whether follow-on breadth is widening."),
                ("round-3", "Confirmation", "Confirm that the signal remains supported."),
                ("round-4", "Crowding", "Watch for crowding and risk-budget saturation."),
                ("round-5", "Exhaustion", "Check whether the expansion is fading or holding."),
            ],
            "bear": [
                ("round-1", "Defensive Open", "Identify which opponents seize control first."),
                ("round-2", "Pressure", "Measure how quickly invalidation pressure spreads."),
                ("round-3", "Containment", "Check whether supporters can stabilize the path."),
                ("round-4", "Breakdown", "Track where the dominant thesis starts to fail."),
                ("round-5", "Stabilization", "Decide whether the bear path stays in control."),
            ],
        }
        selected = round_focus.get(dominant_scenario, round_focus["base"])
        return [
            SimulationRoundPlan(
                round_id=round_id,
                order=index,
                focus=focus,
                objective=objective,
                dominant_scenario=dominant_scenario,
                watchpoints=watchpoints[:3],
                reason_codes=[
                    f"round:{index}",
                    f"scenario:{dominant_scenario}",
                    f"graph_status:{graph_status}",
                ],
            )
            for index, (round_id, focus, objective) in enumerate(selected, start=1)
        ]

    def _allocation_for(self, role: str, authority_weight: float, confidence: float) -> float:
        base = 0.03
        if role == "first_move":
            base = 0.12
        elif role == "follow_on":
            base = 0.07
        return round(min(0.35, base + authority_weight * 0.12 + confidence * 0.08), 2)

    def _persist_run(self, simulation_run: SimulationRun) -> None:
        self._persist_run_payload(asdict(simulation_run))

    def _persist_run_payload(self, payload: dict[str, Any]) -> None:
        target_path = self.runs_root / f"{payload['run_id']}.json"
        target_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _persist_action_log(self, *, run_id: str, round_results) -> Path:
        target_path = self.actions_root / f"{run_id}.jsonl"
        with target_path.open("w", encoding="utf-8") as handle:
            for round_result in round_results:
                for update in round_result.participant_updates:
                    handle.write(
                        json.dumps(
                            {
                                "run_id": run_id,
                                "round_id": round_result.round_id,
                                "order": round_result.order,
                                "participant_id": update.participant_id,
                                "action_type": update.action_type,
                                "reason_codes": list(update.reason_codes),
                                "state_before": update.previous_state,
                                "state_after": update.next_state,
                            },
                            ensure_ascii=False,
                        )
                        + "\n"
                    )
        return target_path

    def _persist_state_snapshots(self, *, run_id: str, round_results) -> list[Path]:
        snapshots: list[Path] = []
        for round_result in round_results:
            target_path = self.snapshots_root / f"{run_id}-{round_result.round_id}.json"
            target_path.write_text(
                json.dumps(
                    {
                        "run_id": run_id,
                        "round_id": round_result.round_id,
                        "order": round_result.order,
                        "participant_states": list(round_result.participant_states),
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            snapshots.append(target_path)
        return snapshots

    def _next_run_id(self, event_id: str) -> str:
        existing = sorted(self.runs_root.glob(f"{event_id}-run-*.json"))
        return f"{event_id}-run-{len(existing) + 1:03d}"

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

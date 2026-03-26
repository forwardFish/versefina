from __future__ import annotations

from domain.belief_graph.service import BeliefGraphService
from domain.event_casebook.service import EventCasebookService
from domain.event_simulation.service import EventSimulationService
from domain.scenario_engine.service import ScenarioEngineService
from schemas.event import EventCardReadModel


class EventCardProjectionService:
    def __init__(
        self,
        *,
        casebook_service: EventCasebookService,
        belief_graph: BeliefGraphService,
        scenario_engine: ScenarioEngineService,
        event_simulation: EventSimulationService | None = None,
    ) -> None:
        self.casebook_service = casebook_service
        self.belief_graph = belief_graph
        self.scenario_engine = scenario_engine
        self.event_simulation = event_simulation

    def present(self, event_id: str) -> EventCardReadModel:
        casebook = self.casebook_service.load_casebook(event_id)
        if casebook is None:
            raise FileNotFoundError(event_id)
        graph_snapshot = self.belief_graph.build_snapshot(event_id)
        scenario_result = self.scenario_engine.build_scenarios(event_id)
        event_summary = str(casebook.structure.get("summary") or casebook.record.get("body") or "").strip()
        participant_summary = self._dedupe(graph_snapshot.key_supporters + graph_snapshot.key_opponents)
        watchpoints = self._dedupe(
            watchpoint
            for scenario in scenario_result.scenarios
            for watchpoint in scenario.watchpoints
        )
        invalidation_conditions = self._dedupe(
            signal
            for scenario in scenario_result.scenarios
            for signal in scenario.invalidation_conditions
        )
        simulation_summary = self._build_simulation_summary(event_id)
        status = "ready" if scenario_result.graph_status != "empty" else "not_ready"
        return EventCardReadModel(
            event_id=event_id,
            status=status,
            event_summary=event_summary,
            participant_summary=participant_summary[:6],
            graph_summary={
                "status": graph_snapshot.status,
                "participant_count": graph_snapshot.participant_count,
                "key_supporters": list(graph_snapshot.key_supporters),
                "key_opponents": list(graph_snapshot.key_opponents),
            },
            scenarios=[scenario.to_dict() for scenario in scenario_result.scenarios],
            simulation_summary=simulation_summary,
            watchpoints=watchpoints[:6],
            invalidation_conditions=invalidation_conditions[:6],
        )

    def _build_simulation_summary(self, event_id: str) -> dict[str, object]:
        if self.event_simulation is None:
            return {}
        latest_run = self.event_simulation.load_latest_run(event_id)
        if latest_run is None:
            return {"status": "simulation_missing"}
        timeline = latest_run.get("timeline") if isinstance(latest_run.get("timeline"), dict) else {}
        return {
            "status": str(latest_run.get("status") or "unknown"),
            "dominant_scenario": str(latest_run.get("dominant_scenario") or ""),
            "round_count": int(latest_run.get("round_count") or 0),
            "timeline_status": str(timeline.get("status") or "timeline_incomplete"),
            "turning_points": list(timeline.get("turning_points") or []),
        }

    def _dedupe(self, values) -> list[str]:
        seen: set[str] = set()
        ordered: list[str] = []
        for value in values:
            normalized = str(value).strip()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            ordered.append(normalized)
        return ordered

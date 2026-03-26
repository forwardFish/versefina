from __future__ import annotations

from domain.belief_graph.service import BeliefGraphService
from domain.event_casebook.service import EventCasebookService
from domain.outcome_review.service import OutcomeReviewService
from domain.event_simulation.service import EventSimulationService
from domain.scenario_engine.service import ScenarioEngineService
from projection.event_cards.service import EventCardProjectionService
from schemas.report import ReportCard, ReviewReport
from schemas.reporting import ReportingBundle, WhyReport


class ReportingError(Exception):
    def __init__(self, *, code: str, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class ReportingService:
    def __init__(
        self,
        *,
        casebook_service: EventCasebookService,
        belief_graph: BeliefGraphService,
        scenario_engine: ScenarioEngineService,
        event_simulation: EventSimulationService,
        outcome_review: OutcomeReviewService,
        event_cards: EventCardProjectionService,
    ) -> None:
        self.casebook_service = casebook_service
        self.belief_graph = belief_graph
        self.scenario_engine = scenario_engine
        self.event_simulation = event_simulation
        self.outcome_review = outcome_review
        self.event_cards = event_cards

    def build_report_card(self, event_id: str) -> ReportCard:
        casebook = self.casebook_service.load_casebook(event_id)
        if casebook is None:
            raise ReportingError(code="EVENT_NOT_FOUND", message="Event casebook not found.", status_code=404)
        card = self.event_cards.present(event_id)
        scenario_result = self.scenario_engine.build_scenarios(event_id)
        simulation_run = self.event_simulation.load_latest_run(event_id)
        return ReportCard(
            event_id=event_id,
            status="ready" if simulation_run is not None else "degraded",
            event_summary=card.event_summary,
            graph_summary={
                **card.graph_summary,
                "graph_status": scenario_result.graph_status,
                "dominant_scenario": scenario_result.dominant_scenario,
            },
            scenarios=[scenario.to_dict() for scenario in scenario_result.scenarios],
            simulation_summary=card.simulation_summary,
        )

    def build_review_report(self, event_id: str) -> ReviewReport:
        casebook = self.casebook_service.load_casebook(event_id)
        if casebook is None:
            raise ReportingError(code="EVENT_NOT_FOUND", message="Event casebook not found.", status_code=404)
        simulation_run = self.event_simulation.load_latest_run(event_id)
        if simulation_run is None:
            timeline: dict[str, object] = {"status": "simulation_missing"}
            key_reasons: list[str] = []
        else:
            timeline = simulation_run.get("timeline") if isinstance(simulation_run.get("timeline"), dict) else {}
            key_reasons = self._collect_key_reasons(simulation_run)
        invalidation_points = list(casebook.structure.get("invalidation_conditions") or [])
        latest_outcome = self.outcome_review.load_latest_outcome(event_id)
        why_context = {
            "event_id": event_id,
            "timeline_status": str(timeline.get("status") or "timeline_incomplete"),
            "dominant_scenario": str((simulation_run or {}).get("dominant_scenario") or ""),
            "actual_outcome": latest_outcome.dominant_scenario_actual if latest_outcome is not None else "",
            "score_label": latest_outcome.score_label if latest_outcome is not None else "",
            "key_reasons": key_reasons,
        }
        return ReviewReport(
            event_id=event_id,
            status="ready" if simulation_run is not None else "degraded",
            timeline=timeline,
            outcome=latest_outcome.to_dict() if latest_outcome is not None else {"status": "outcome_missing"},
            key_reasons=key_reasons,
            invalidation_points=invalidation_points,
            why_context=why_context,
        )

    def build_bundle(self, event_id: str) -> ReportingBundle:
        report_card = self.build_report_card(event_id)
        review_report = self.build_review_report(event_id)
        return ReportingBundle(
            event_id=event_id,
            report_card=report_card,
            review_report=review_report,
            why_context=review_report.why_context,
        )

    def build_why_report(self, event_id: str) -> WhyReport:
        casebook = self.casebook_service.load_casebook(event_id)
        if casebook is None:
            raise ReportingError(code="EVENT_NOT_FOUND", message="Event casebook not found.", status_code=404)

        graph_snapshot = self.belief_graph.build_snapshot(event_id)
        scenario_result = self.scenario_engine.build_scenarios(event_id)
        simulation_run = self.event_simulation.load_latest_run(event_id)
        latest_outcome = self.outcome_review.load_latest_outcome(event_id)
        reliability = self.outcome_review.build_reliability_summary(event_id)
        evidence = {
            "beliefs": {
                "status": graph_snapshot.status,
                "key_supporters": list(graph_snapshot.key_supporters),
                "key_opponents": list(graph_snapshot.key_opponents),
                "consensus_signals": list(graph_snapshot.consensus_signals),
                "divergence_signals": list(graph_snapshot.divergence_signals),
            },
            "scenarios": {
                "dominant_scenario": scenario_result.dominant_scenario,
                "graph_status": scenario_result.graph_status,
            },
            "simulation": {
                "status": str((simulation_run or {}).get("status") or "missing"),
                "timeline_status": str(((simulation_run or {}).get("timeline") or {}).get("status") or "missing"),
                "turning_points": list((((simulation_run or {}).get("timeline") or {}).get("turning_points") or [])),
                "action_log_path": str((simulation_run or {}).get("action_log_path") or ""),
                "key_reasons": self._collect_key_reasons(simulation_run or {}),
            },
            "outcome": latest_outcome.to_dict() if latest_outcome is not None else {"status": "outcome_missing"},
            "reliability": reliability.to_dict(),
        }
        gaps: list[str] = []
        if simulation_run is None:
            gaps.append("simulation_missing")
        if latest_outcome is None:
            gaps.append("outcome_missing")
        if not evidence["beliefs"]["consensus_signals"] and not evidence["beliefs"]["divergence_signals"]:
            gaps.append("belief_signal_thin")
        if gaps and simulation_run is None and latest_outcome is None:
            return WhyReport(
                event_id=event_id,
                status="insufficient_evidence",
                answer="Insufficient evidence to explain the event yet; simulation logs and outcome backfill are both missing.",
                dominant_scenario=scenario_result.dominant_scenario,
                actual_outcome="",
                score_label="",
                evidence=evidence,
                gaps=gaps,
            )

        answer_parts = [
            (
                f"The workflow leaned {scenario_result.dominant_scenario} because supporters "
                f"{', '.join(graph_snapshot.key_supporters[:2]) or 'were limited'} and consensus signals "
                f"{', '.join(graph_snapshot.consensus_signals[:2]) or 'were thin'}."
            )
        ]
        if latest_outcome is not None:
            answer_parts.append(
                f"At {latest_outcome.horizon.upper()}, the realized path resolved as "
                f"{latest_outcome.dominant_scenario_actual} with score {latest_outcome.score_label}."
            )
            if latest_outcome.failure_reasons:
                answer_parts.append(
                    f"The main failure reasons were {', '.join(latest_outcome.failure_reasons[:3])}."
                )
        key_reasons = evidence["simulation"]["key_reasons"]
        if key_reasons:
            answer_parts.append(f"Simulation logs highlighted {', '.join(key_reasons[:3])}.")
        return WhyReport(
            event_id=event_id,
            status="ready",
            answer=" ".join(answer_parts),
            dominant_scenario=scenario_result.dominant_scenario,
            actual_outcome=latest_outcome.dominant_scenario_actual if latest_outcome is not None else "",
            score_label=latest_outcome.score_label if latest_outcome is not None else "",
            evidence=evidence,
            gaps=gaps,
        )

    def _collect_key_reasons(self, simulation_run: dict[str, object]) -> list[str]:
        round_results = simulation_run.get("round_results") if isinstance(simulation_run.get("round_results"), list) else []
        ordered: list[str] = []
        seen: set[str] = set()
        for round_result in round_results:
            if not isinstance(round_result, dict):
                continue
            for update in round_result.get("participant_updates") or []:
                if not isinstance(update, dict):
                    continue
                for reason in update.get("reason_codes") or []:
                    normalized = str(reason).strip()
                    if not normalized or normalized in seen:
                        continue
                    seen.add(normalized)
                    ordered.append(normalized)
        return ordered[:8]

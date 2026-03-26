from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
from typing import Any

from domain.belief_graph.service import BeliefGraphService
from domain.event_casebook.service import EventCasebookService
from domain.event_ingestion.service import EventIngestionService
from domain.event_simulation.service import EventSimulationService
from domain.event_structuring.service import EventStructuringService
from domain.influence_graph.service import InfluenceGraphService
from domain.outcome_review.service import OutcomeReviewService
from domain.participant_preparation.service import ParticipantPreparationError, ParticipantPreparationService
from domain.reporting.service import ReportingError, ReportingService
from domain.scenario_engine.service import ScenarioEngineService
from domain.theme_mapping.service import ThemeMappingService
from schemas.event_sandbox import (
    BeliefRoundSnapshot,
    MarketStateSnapshot,
    ParticipantAction,
    ReplayPayload,
    RoundSnapshot,
    ScenarioRoundSnapshot,
    SimulationSummaryPayload,
    ValidationPayload,
)


_SUPPORTIVE_STANCES = {"bullish", "constructive"}
_OPPOSING_STANCES = {"watch", "skeptical", "bearish"}
_ACTIVE_STATES = {"monitoring", "engaged", "confirmed", "accelerating", "confirming", "scaling", "challenging", "hedging", "de_risking"}


class EventSandboxError(Exception):
    def __init__(self, *, code: str, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class EventSandboxService:
    def __init__(
        self,
        *,
        runtime_root: Path,
        event_ingestion: EventIngestionService,
        event_structuring: EventStructuringService,
        theme_mapping: ThemeMappingService,
        event_casebook: EventCasebookService,
        participant_preparation: ParticipantPreparationService,
        belief_graph: BeliefGraphService,
        scenario_engine: ScenarioEngineService,
        influence_graph: InfluenceGraphService,
        event_simulation: EventSimulationService,
        reporting: ReportingService,
        outcome_review: OutcomeReviewService,
    ) -> None:
        self.runtime_root = runtime_root
        self.event_ingestion = event_ingestion
        self.event_structuring = event_structuring
        self.theme_mapping = theme_mapping
        self.event_casebook = event_casebook
        self.participant_preparation = participant_preparation
        self.belief_graph = belief_graph
        self.scenario_engine = scenario_engine
        self.influence_graph = influence_graph
        self.event_simulation = event_simulation
        self.reporting = reporting
        self.outcome_review = outcome_review

    def structure_event(self, event_id: str) -> dict[str, Any]:
        casebook = self.event_casebook.load_casebook(event_id)
        if casebook is None:
            record = self.event_ingestion.load_record(event_id)
            if record is None:
                raise EventSandboxError(
                    code="EVENT_NOT_FOUND",
                    message="Event record not found.",
                    status_code=404,
                )
            structure = self.event_structuring.structure_event(record)
            mapping = self.theme_mapping.map_structure(structure)
            casebook = self.event_casebook.write_casebook(
                record=record,
                structure=structure,
                mapping=mapping,
                status="structured",
            )
        return {
            "event_id": event_id,
            "status": "structured",
            "record": dict(casebook.record),
            "structure": dict(casebook.structure),
            "mapping": dict(casebook.mapping),
        }

    def prepare_participants(self, event_id: str) -> dict[str, Any]:
        try:
            prepared = self.participant_preparation.prepare_event(event_id)
        except ParticipantPreparationError as exc:
            raise EventSandboxError(code=exc.code, message=exc.message, status_code=exc.status_code) from exc
        return asdict(prepared)

    def load_participants(self, event_id: str) -> dict[str, Any]:
        try:
            prepared = self.participant_preparation.prepare_event(event_id)
        except ParticipantPreparationError:
            return {"event_id": event_id, "status": "not_found", "participants": []}
        roster = dict(prepared.participant_roster or {})
        return {
            "event_id": event_id,
            "status": str(roster.get("status") or prepared.status or "unknown"),
            "participants": list(roster.get("participants") or []),
            "blocked_reasons": list(roster.get("blocked_reasons") or []),
            "activation_basis": list(roster.get("activation_basis") or []),
            "casebook_status": str((prepared.casebook or {}).get("status") or ""),
        }

    def simulate_event(self, event_id: str) -> dict[str, Any]:
        return self.event_simulation.run_simulation(event_id).to_dict()

    def load_simulation(self, event_id: str) -> dict[str, Any]:
        run = self.event_simulation.load_latest_run(event_id)
        if run is None:
            return SimulationSummaryPayload(event_id=event_id, status="simulation_missing").to_dict()
        round_snapshots = self._load_round_snapshots(event_id, run)
        latest_round = round_snapshots[-1] if round_snapshots else None
        top_participants = sorted(
            list((latest_round.participant_states if latest_round else run.get("participant_states") or [])),
            key=lambda item: (-float(item.get("authority_weight") or 0.0), -float(item.get("confidence") or 0.0)),
        )[:6]
        return SimulationSummaryPayload(
            event_id=event_id,
            status="ready",
            run_id=str(run.get("run_id") or ""),
            dominant_scenario=str(run.get("dominant_scenario") or ""),
            round_count=int(run.get("round_count") or len(round_snapshots)),
            latest_market_state=str(((latest_round.market_state.to_dict() if latest_round and latest_round.market_state else {}) or {}).get("state") or ""),
            timeline=dict(run.get("timeline") or {}),
            top_participants=top_participants,
            rounds=[
                {
                    "round_id": item.round_id,
                    "order": item.order,
                    "focus": item.focus,
                    "market_state": (item.market_state.to_dict() if item.market_state else {}),
                    "scenario_snapshot": (item.scenario_snapshot.to_dict() if item.scenario_snapshot else {}),
                    "turning_point": item.turning_point,
                }
                for item in round_snapshots
            ],
        ).to_dict()

    def load_rounds(self, event_id: str) -> dict[str, Any]:
        run = self.event_simulation.load_latest_run(event_id)
        if run is None:
            return {"event_id": event_id, "status": "simulation_missing", "rounds": []}
        round_snapshots = self._load_round_snapshots(event_id, run)
        return {
            "event_id": event_id,
            "status": "ready",
            "run_id": str(run.get("run_id") or ""),
            "rounds": [item.to_dict() for item in round_snapshots],
        }

    def load_round(self, event_id: str, round_key: str) -> dict[str, Any]:
        run = self.event_simulation.load_latest_run(event_id)
        if run is None:
            return {"event_id": event_id, "status": "simulation_missing"}
        round_snapshots = self._load_round_snapshots(event_id, run)
        resolved = self._find_round(round_snapshots, round_key)
        if resolved is None:
            return {"event_id": event_id, "status": "not_found", "round_id": round_key}
        return resolved.to_dict()

    def load_influence_graph(self, event_id: str) -> dict[str, Any]:
        run = self.event_simulation.load_latest_run(event_id)
        if run is None:
            return {"event_id": event_id, "status": "simulation_missing", "rounds": []}
        round_snapshots = self._load_round_snapshots(event_id, run)
        payload = self.influence_graph.build_payload(
            event_id,
            [
                {
                    "round_id": item.round_id,
                    "order": item.order,
                    "participant_actions": [action.to_dict() for action in item.participant_actions],
                    "participant_states": list(item.participant_states),
                    "market_state": item.market_state.to_dict() if item.market_state else {},
                }
                for item in round_snapshots
            ],
        )
        return payload.to_dict()

    def load_influence_graph_round(self, event_id: str, round_key: str) -> dict[str, Any]:
        payload = self.load_influence_graph(event_id)
        if payload.get("status") != "ready":
            return payload
        for round_item in payload.get("rounds") or []:
            if self._round_matches(round_item.get("round_id"), round_item.get("order"), round_key):
                return round_item
        return {"event_id": event_id, "status": "not_found", "round_id": round_key}

    def load_belief(self, event_id: str) -> dict[str, Any]:
        run = self.event_simulation.load_latest_run(event_id)
        if run is None:
            return {"event_id": event_id, "status": "simulation_missing", "rounds": []}
        round_snapshots = self._load_round_snapshots(event_id, run)
        rounds = [item.belief_snapshot.to_dict() for item in round_snapshots if item.belief_snapshot is not None]
        return {
            "event_id": event_id,
            "status": "ready",
            "latest_round_id": rounds[-1]["round_id"] if rounds else "",
            "latest": rounds[-1] if rounds else {},
            "rounds": rounds,
        }

    def load_belief_round(self, event_id: str, round_key: str) -> dict[str, Any]:
        payload = self.load_belief(event_id)
        if payload.get("status") != "ready":
            return payload
        for round_item in payload.get("rounds") or []:
            if self._round_matches(round_item.get("round_id"), round_item.get("order"), round_key):
                return round_item
        return {"event_id": event_id, "status": "not_found", "round_id": round_key}

    def load_scenarios(self, event_id: str) -> dict[str, Any]:
        run = self.event_simulation.load_latest_run(event_id)
        if run is None:
            return {"event_id": event_id, "status": "simulation_missing", "rounds": []}
        round_snapshots = self._load_round_snapshots(event_id, run)
        rounds = [item.scenario_snapshot.to_dict() for item in round_snapshots if item.scenario_snapshot is not None]
        return {
            "event_id": event_id,
            "status": "ready",
            "latest_round_id": rounds[-1]["round_id"] if rounds else "",
            "latest": rounds[-1] if rounds else {},
            "rounds": rounds,
        }

    def load_scenario_round(self, event_id: str, round_key: str) -> dict[str, Any]:
        payload = self.load_scenarios(event_id)
        if payload.get("status") != "ready":
            return payload
        for round_item in payload.get("rounds") or []:
            if self._round_matches(round_item.get("round_id"), round_item.get("order"), round_key):
                return round_item
        return {"event_id": event_id, "status": "not_found", "round_id": round_key}

    def load_replay(self, event_id: str) -> dict[str, Any]:
        run = self.event_simulation.load_latest_run(event_id)
        if run is None:
            return ReplayPayload(event_id=event_id, status="simulation_missing").to_dict()
        round_snapshots = self._load_round_snapshots(event_id, run)
        return ReplayPayload(
            event_id=event_id,
            status="ready",
            run_id=str(run.get("run_id") or ""),
            dominant_scenario=str(run.get("dominant_scenario") or ""),
            timeline=dict(run.get("timeline") or {}),
            rounds=[item.to_dict() for item in round_snapshots],
        ).to_dict()

    def load_report(self, event_id: str) -> dict[str, Any]:
        report_card: dict[str, Any]
        review_report: dict[str, Any]
        try:
            report_card = self.reporting.build_report_card(event_id).to_dict()
            review_report = self.reporting.build_review_report(event_id).to_dict()
        except ReportingError as exc:
            return {
                "event_id": event_id,
                "status": "not_found",
                "error_code": exc.code,
                "error_message": exc.message,
            }
        return {
            "event_id": event_id,
            "status": "ready",
            "report_card": report_card,
            "review_report": review_report,
        }

    def load_validation(self, event_id: str) -> dict[str, Any]:
        try:
            report = self.load_report(event_id)
            why_report = self.reporting.build_why_report(event_id).to_dict()
            outcomes = {
                "event_id": event_id,
                "status": "ready",
                "outcomes": [item.to_dict() for item in self.outcome_review.list_outcomes(event_id)],
            }
            if not outcomes["outcomes"]:
                outcomes["status"] = "outcome_missing"
            reliability = self.outcome_review.build_reliability_summary(event_id).to_dict()
        except ReportingError as exc:
            return {"event_id": event_id, "status": "not_found", "error_code": exc.code, "error_message": exc.message}
        except Exception:
            reliability = {"event_id": event_id, "status": "not_found", "participants": []}
            outcomes = {"event_id": event_id, "status": "outcome_missing", "outcomes": []}
            why_report = {}
            report = {"event_id": event_id, "status": "degraded", "report_card": {}, "review_report": {}}
        return ValidationPayload(
            event_id=event_id,
            status="ready" if report.get("status") == "ready" else str(report.get("status") or "degraded"),
            report=report,
            why=why_report,
            outcomes=outcomes,
            reliability=reliability,
        ).to_dict()

    def _load_round_snapshots(self, event_id: str, run: dict[str, Any]) -> list[RoundSnapshot]:
        round_results = list(run.get("round_results") or [])
        if not round_results:
            return []
        try:
            scenario_pack = self.scenario_engine.build_scenarios(event_id)
        except Exception:
            scenario_pack = None

        prepared = self.load_participants(event_id)
        previous_market_state = "DORMANT"
        interim_rounds: list[dict[str, Any]] = []

        for index, round_result in enumerate(round_results, start=1):
            participant_states = list(round_result.get("participant_states") or [])
            actions = [self._build_action_payload(update, participant_states) for update in round_result.get("participant_updates") or []]
            belief = self._build_belief_snapshot(event_id, round_result, participant_states)
            market_state = self._build_market_state_snapshot(
                event_id=event_id,
                round_result=round_result,
                belief=belief,
                previous_state=previous_market_state,
                is_last=index == len(round_results),
            )
            scenario_snapshot = self._build_scenario_round_snapshot(
                event_id=event_id,
                round_result=round_result,
                belief=belief,
                market_state=market_state,
                scenario_pack=scenario_pack.to_dict() if scenario_pack is not None else {},
            )
            interim_rounds.append(
                {
                    "event_id": event_id,
                    "run_id": str(run.get("run_id") or ""),
                    "round_id": str(round_result.get("round_id") or f"round-{index}"),
                    "order": int(round_result.get("order") or index),
                    "focus": str(round_result.get("focus") or ""),
                    "objective": str(round_result.get("objective") or ""),
                    "participant_actions": [item.to_dict() for item in actions],
                    "participant_states": participant_states,
                    "belief_snapshot": belief.to_dict(),
                    "market_state": market_state.to_dict(),
                    "scenario_snapshot": scenario_snapshot.to_dict(),
                    "turning_point": str(round_result.get("round_id") or "") in list((run.get("timeline") or {}).get("turning_points") or []),
                    "prepared_participants": list(prepared.get("participants") or []),
                }
            )
            previous_market_state = market_state.state

        influence_payload = self.influence_graph.build_payload(event_id, interim_rounds).to_dict()
        edges_by_round = {
            str(item.get("round_id") or ""): list(item.get("edges") or [])
            for item in influence_payload.get("rounds") or []
        }

        snapshots: list[RoundSnapshot] = []
        for round_item in interim_rounds:
            snapshot = RoundSnapshot(
                event_id=event_id,
                run_id=str(round_item["run_id"]),
                round_id=str(round_item["round_id"]),
                order=int(round_item["order"]),
                focus=str(round_item["focus"]),
                objective=str(round_item["objective"]),
                participant_actions=[ParticipantAction(**item) for item in round_item["participant_actions"]],
                participant_states=list(round_item["participant_states"]),
                influence_edges=[
                    edge if hasattr(edge, "to_dict") else edge
                    for edge in []
                ],
                belief_snapshot=BeliefRoundSnapshot(**round_item["belief_snapshot"]),
                market_state=MarketStateSnapshot(**round_item["market_state"]),
                scenario_snapshot=ScenarioRoundSnapshot(**round_item["scenario_snapshot"]),
                turning_point=bool(round_item["turning_point"]),
            )
            edge_payloads = []
            for edge in edges_by_round.get(snapshot.round_id, []):
                edge_payloads.append(edge)
            snapshot_dict = snapshot.to_dict()
            snapshot_dict["influence_edges"] = edge_payloads
            self._persist_round_snapshot(run_id=snapshot.run_id, round_id=snapshot.round_id, payload=snapshot_dict)
            snapshots.append(
                RoundSnapshot(
                    event_id=snapshot.event_id,
                    run_id=snapshot.run_id,
                    round_id=snapshot.round_id,
                    order=snapshot.order,
                    focus=snapshot.focus,
                    objective=snapshot.objective,
                    participant_actions=snapshot.participant_actions,
                    participant_states=snapshot.participant_states,
                    influence_edges=[],
                    belief_snapshot=snapshot.belief_snapshot,
                    market_state=snapshot.market_state,
                    scenario_snapshot=snapshot.scenario_snapshot,
                    turning_point=snapshot.turning_point,
                )
            )

        enriched: list[RoundSnapshot] = []
        for snapshot in snapshots:
            payload = self._load_persisted_round_snapshot(snapshot.run_id, snapshot.round_id)
            edges = list(payload.get("influence_edges") or []) if isinstance(payload, dict) else []
            enriched.append(
                RoundSnapshot(
                    event_id=snapshot.event_id,
                    run_id=snapshot.run_id,
                    round_id=snapshot.round_id,
                    order=snapshot.order,
                    focus=snapshot.focus,
                    objective=snapshot.objective,
                    participant_actions=snapshot.participant_actions,
                    participant_states=snapshot.participant_states,
                    influence_edges=edges,
                    belief_snapshot=snapshot.belief_snapshot,
                    market_state=snapshot.market_state,
                    scenario_snapshot=snapshot.scenario_snapshot,
                    turning_point=snapshot.turning_point,
                )
            )
        return enriched

    def _build_action_payload(self, update: dict[str, Any], participant_states: list[dict[str, Any]]) -> ParticipantAction:
        participant_id = str(update.get("participant_id") or "")
        state = next((item for item in participant_states if str(item.get("participant_id") or "") == participant_id), {})
        stance = str(state.get("stance") or "").strip().lower()
        action_type = str(update.get("action_type") or "")
        polarity = "neutral"
        if action_type in {"risk_watch", "exit"} or stance in _OPPOSING_STANCES:
            polarity = "bearish"
        elif stance in _SUPPORTIVE_STANCES:
            polarity = "bullish"
        return ParticipantAction(
            participant_id=participant_id,
            participant_family=str(state.get("participant_family") or "unknown"),
            action_type=action_type,
            action_name=str(update.get("action_name") or ""),
            actor_id=str(update.get("actor_id") or participant_id),
            target_id=str(update.get("target_id") or ""),
            confidence=float(update.get("confidence") or 0.0),
            reason_code=str(update.get("reason_code") or ""),
            previous_state=str(update.get("previous_state") or ""),
            next_state=str(update.get("next_state") or ""),
            polarity=polarity,
            reason_codes=list(update.get("reason_codes") or []),
        )

    def _build_belief_snapshot(
        self,
        event_id: str,
        round_result: dict[str, Any],
        participant_states: list[dict[str, Any]],
    ) -> BeliefRoundSnapshot:
        supportive = [item for item in participant_states if str(item.get("stance") or "").strip().lower() in _SUPPORTIVE_STANCES]
        opposing = [item for item in participant_states if str(item.get("stance") or "").strip().lower() in _OPPOSING_STANCES]
        total_weight = sum(float(item.get("authority_weight") or 0.0) * max(float(item.get("confidence") or 0.0), 0.01) for item in participant_states) or 1.0
        supportive_weight = sum(float(item.get("authority_weight") or 0.0) * max(float(item.get("confidence") or 0.0), 0.01) for item in supportive)
        opposing_weight = sum(float(item.get("authority_weight") or 0.0) * max(float(item.get("confidence") or 0.0), 0.01) for item in opposing)
        consensus_strength = round(min(0.99, supportive_weight / total_weight), 2)
        opposition_strength = round(min(0.99, opposing_weight / total_weight), 2)
        divergence_index = round(min(0.99, min(consensus_strength, opposition_strength) + (0.08 if supportive and opposing else 0.0)), 2)
        key_supporters = [
            str(item.get("participant_family") or item.get("participant_id") or "")
            for item in sorted(supportive, key=lambda row: (-float(row.get("authority_weight") or 0.0), -float(row.get("confidence") or 0.0)))[:3]
        ]
        key_opponents = [
            str(item.get("participant_family") or item.get("participant_id") or "")
            for item in sorted(opposing, key=lambda row: (-float(row.get("authority_weight") or 0.0), -float(row.get("confidence") or 0.0)))[:3]
        ]
        summary = "Supportive participants still lead the transmission path." if consensus_strength >= opposition_strength else "Opposition and invalidation pressure are catching up."
        return BeliefRoundSnapshot(
            event_id=event_id,
            round_id=str(round_result.get("round_id") or ""),
            order=int(round_result.get("order") or 0),
            consensus_strength=consensus_strength,
            opposition_strength=opposition_strength,
            divergence_index=divergence_index,
            key_supporters=key_supporters,
            key_opponents=key_opponents,
            summary=summary,
        )

    def _build_market_state_snapshot(
        self,
        *,
        event_id: str,
        round_result: dict[str, Any],
        belief: BeliefRoundSnapshot,
        previous_state: str,
        is_last: bool,
    ) -> MarketStateSnapshot:
        participant_states = list(round_result.get("participant_states") or [])
        updates = list(round_result.get("participant_updates") or [])
        active_count = sum(1 for item in participant_states if str(item.get("state") or "") in _ACTIVE_STATES)
        follow_on_count = sum(1 for item in updates if str(item.get("action_type") or "") == "follow_on")
        exit_count = sum(1 for item in updates if str(item.get("action_type") or "") == "exit")
        first_move_count = sum(1 for item in updates if str(item.get("action_type") or "") == "first_move")

        state = previous_state
        if int(round_result.get("order") or 0) == 1 and first_move_count:
            state = "IGNITION"
        elif previous_state in {"DORMANT", "IGNITION"} and follow_on_count >= 1 and active_count >= 2:
            state = "PROPAGATING"
        elif previous_state == "PROPAGATING" and follow_on_count >= 2 and belief.consensus_strength >= 0.55 and exit_count == 0:
            state = "CROWDED"
        elif exit_count >= 1 or belief.divergence_index >= 0.3:
            state = "FRAGILE"
        if (is_last and state == "FRAGILE" and exit_count >= 2) or belief.opposition_strength > belief.consensus_strength + 0.1:
            state = "INVALIDATED"
        if not active_count and not first_move_count and previous_state == "DORMANT":
            state = "DORMANT"

        summary = {
            "IGNITION": "First movers are reacting and the signal has started to spread.",
            "PROPAGATING": "Follow-on participants are confirming the signal across the roster.",
            "CROWDED": "The same thesis is becoming crowded and breadth is saturating.",
            "FRAGILE": "Exit pressure and divergence are making the path fragile.",
            "INVALIDATED": "Risk pressure overtook the supportive path and the thesis is breaking.",
            "DORMANT": "The market has not activated into a meaningful simulation path yet.",
        }.get(state, "The market state is being monitored.")
        return MarketStateSnapshot(
            event_id=event_id,
            round_id=str(round_result.get("round_id") or ""),
            order=int(round_result.get("order") or 0),
            state=state,
            active_participant_count=active_count,
            exit_count=exit_count,
            follow_on_count=follow_on_count,
            summary=summary,
        )

    def _build_scenario_round_snapshot(
        self,
        *,
        event_id: str,
        round_result: dict[str, Any],
        belief: BeliefRoundSnapshot,
        market_state: MarketStateSnapshot,
        scenario_pack: dict[str, Any],
    ) -> ScenarioRoundSnapshot:
        bull_score = 0.35 + belief.consensus_strength * 0.65
        base_score = 0.42 + max(0.0, 0.22 - abs(belief.consensus_strength - belief.opposition_strength))
        bear_score = 0.28 + belief.opposition_strength * 0.7

        if market_state.state == "PROPAGATING":
            bull_score += 0.18
        elif market_state.state == "CROWDED":
            bull_score += 0.1
            bear_score += 0.05
        elif market_state.state == "FRAGILE":
            bear_score += 0.18
            bull_score -= 0.08
        elif market_state.state == "INVALIDATED":
            bear_score += 0.3
            bull_score -= 0.14

        scores = {
            "bull": max(0.05, bull_score),
            "base": max(0.05, base_score),
            "bear": max(0.05, bear_score),
        }
        total = sum(scores.values()) or 1.0
        bull_confidence = round(scores["bull"] / total, 2)
        base_confidence = round(scores["base"] / total, 2)
        bear_confidence = round(scores["bear"] / total, 2)
        dominant_scenario = max(
            (("bull", bull_confidence), ("base", base_confidence), ("bear", bear_confidence)),
            key=lambda item: item[1],
        )[0]
        scenario_lookup = {
            str(item.get("scenario_id") or ""): item for item in scenario_pack.get("scenarios") or []
        }
        selected = scenario_lookup.get(dominant_scenario, {})
        summary = {
            "bull": "Supportive breadth keeps the bullish path in control.",
            "base": "The path is balanced enough that the base case remains dominant.",
            "bear": "Invalidation pressure now dominates the path.",
        }.get(dominant_scenario, "The scenario pack is being monitored.")
        return ScenarioRoundSnapshot(
            event_id=event_id,
            round_id=str(round_result.get("round_id") or ""),
            order=int(round_result.get("order") or 0),
            dominant_scenario=dominant_scenario,
            bull_confidence=bull_confidence,
            base_confidence=base_confidence,
            bear_confidence=bear_confidence,
            summary=summary,
            watchpoints=list(selected.get("watchpoints") or []),
            invalidation_conditions=list(selected.get("invalidation_conditions") or []),
        )

    def _persist_round_snapshot(self, *, run_id: str, round_id: str, payload: dict[str, Any]) -> None:
        target_path = self.event_simulation.snapshots_root / f"{run_id}-{round_id}.json"
        target_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _load_persisted_round_snapshot(self, run_id: str, round_id: str) -> dict[str, Any]:
        target_path = self.event_simulation.snapshots_root / f"{run_id}-{round_id}.json"
        if not target_path.exists():
            return {}
        return json.loads(target_path.read_text(encoding="utf-8"))

    def _find_round(self, round_snapshots: list[RoundSnapshot], round_key: str) -> RoundSnapshot | None:
        for item in round_snapshots:
            if self._round_matches(item.round_id, item.order, round_key):
                return item
        return None

    def _round_matches(self, round_id: str | None, order: int | None, round_key: str | None) -> bool:
        resolved_key = str(round_key or "").strip().lower()
        if not resolved_key:
            return False
        if str(round_id or "").strip().lower() == resolved_key:
            return True
        if resolved_key.isdigit() and int(resolved_key) == int(order or 0):
            return True
        if resolved_key.startswith("round-") and str(round_id or "").strip().lower() == resolved_key:
            return True
        return False

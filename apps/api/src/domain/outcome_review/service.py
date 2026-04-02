from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path

from domain.event_casebook.service import EventCasebookService
from domain.event_simulation.service import EventSimulationService
from domain.scenario_engine.service import ScenarioEngineService
from schemas.command import OutcomeReviewWriteRequest
from schemas.outcome_review import OutcomeReview
from schemas.reliability import ParticipantReliability, ReliabilitySummary

_POSITIVE_SIGNALS = {
    "outperform",
    "positive",
    "strong",
    "confirmed",
    "supportive",
    "broadening",
    "expanding",
    "heated",
    "bullish",
}
_NEGATIVE_SIGNALS = {
    "underperform",
    "negative",
    "weak",
    "failed",
    "rejected",
    "narrowing",
    "contracting",
    "cooled",
    "bearish",
    "collapsed",
}
_SUPPORTIVE_STANCES = {"bullish", "constructive"}
_DEFENSIVE_STANCES = {"watch", "skeptical", "bearish", "neutral"}
_HORIZON_ORDER = {"t1": 1, "t3": 2}


class OutcomeReviewError(Exception):
    def __init__(self, *, code: str, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class OutcomeReviewService:
    def __init__(
        self,
        *,
        runtime_root: Path,
        casebook_service: EventCasebookService,
        scenario_engine: ScenarioEngineService,
        event_simulation: EventSimulationService,
    ) -> None:
        self.runtime_root = runtime_root
        self.casebook_service = casebook_service
        self.scenario_engine = scenario_engine
        self.event_simulation = event_simulation
        self.outcomes_root = runtime_root / "outcomes"
        self.outcomes_root.mkdir(parents=True, exist_ok=True)

    def record_outcome(self, event_id: str, payload: OutcomeReviewWriteRequest) -> OutcomeReview:
        casebook = self.casebook_service.load_casebook(event_id)
        if casebook is None:
            raise OutcomeReviewError(
                code="EVENT_NOT_FOUND",
                message="Event casebook not found.",
                status_code=404,
            )

        horizon = self._normalize_horizon(payload.horizon)
        simulation_run = self.event_simulation.load_latest_run(event_id)
        predicted_scenario = str((simulation_run or {}).get("dominant_scenario") or "").strip()
        if not predicted_scenario:
            predicted_scenario = self.scenario_engine.build_scenarios(event_id).dominant_scenario

        dominant_scenario_actual = self._derive_actual_scenario(
            sector_performance=payload.sector_performance,
            leader_performance=payload.leader_performance,
            expansion_status=payload.expansion_status,
            sentiment_status=payload.sentiment_status,
        )
        failure_reasons = self._collect_failure_reasons(
            predicted_scenario=predicted_scenario,
            actual_scenario=dominant_scenario_actual,
            sector_performance=payload.sector_performance,
            leader_performance=payload.leader_performance,
            expansion_status=payload.expansion_status,
            sentiment_status=payload.sentiment_status,
        )
        score_label = self._derive_score_label(
            predicted_scenario=predicted_scenario,
            actual_scenario=dominant_scenario_actual,
            horizon=horizon,
            failure_reasons=failure_reasons,
        )
        outcome = OutcomeReview(
            event_id=event_id,
            horizon=horizon,
            sector_performance=payload.sector_performance,
            leader_performance=payload.leader_performance,
            expansion_status=payload.expansion_status,
            sentiment_status=payload.sentiment_status,
            dominant_scenario_actual=dominant_scenario_actual,
            score_label=score_label,
            predicted_scenario=predicted_scenario,
            status="ready",
            event_type=str(casebook.structure.get("event_type") or ""),
            source_run_id=str((simulation_run or {}).get("run_id") or ""),
            analyst_note=payload.analyst_note.strip(),
            recorded_at=self._now_iso(),
            failure_reasons=failure_reasons,
            supporting_evidence=self._collect_supporting_evidence(
                payload=payload,
                predicted_scenario=predicted_scenario,
                actual_scenario=dominant_scenario_actual,
            ),
        )
        self._persist_outcome(outcome)
        return outcome

    def load_outcome(self, event_id: str, horizon: str) -> OutcomeReview | None:
        target_path = self.outcomes_root / f"{event_id}-{self._normalize_horizon(horizon)}.json"
        if not target_path.exists():
            return None
        return OutcomeReview(**json.loads(target_path.read_text(encoding="utf-8")))

    def list_outcomes(self, event_id: str) -> list[OutcomeReview]:
        outcomes: list[OutcomeReview] = []
        for path in sorted(self.outcomes_root.glob(f"{event_id}-*.json")):
            outcomes.append(OutcomeReview(**json.loads(path.read_text(encoding="utf-8"))))
        return sorted(
            outcomes,
            key=lambda item: (_HORIZON_ORDER.get(item.horizon, 99), item.recorded_at),
        )

    def load_latest_outcome(self, event_id: str) -> OutcomeReview | None:
        outcomes = self.list_outcomes(event_id)
        if not outcomes:
            return None
        return sorted(
            outcomes,
            key=lambda item: (_HORIZON_ORDER.get(item.horizon, 99), item.recorded_at),
            reverse=True,
        )[0]

    def build_reliability_summary(self, event_id: str) -> ReliabilitySummary:
        casebook = self.casebook_service.load_casebook(event_id)
        if casebook is None:
            raise OutcomeReviewError(
                code="EVENT_NOT_FOUND",
                message="Event casebook not found.",
                status_code=404,
            )

        event_type = str(casebook.structure.get("event_type") or "")
        by_family: dict[str, dict[str, float | int | str]] = defaultdict(
            lambda: {
                "sample_size": 0,
                "direction_correct": 0.0,
                "early_detection": 0.0,
                "invalidation_detection": 0.0,
                "last_score_label": "",
            }
        )

        for outcome in self._iter_event_type_outcomes(event_type):
            run = self.event_simulation.load_latest_run(outcome.event_id)
            if run is None:
                continue
            early_detection_ids, invalidation_ids = self._extract_detection_ids(run)
            participants = run.get("participant_states") if isinstance(run.get("participant_states"), list) else []
            family_participants: dict[str, list[dict[str, object]]] = defaultdict(list)
            for participant in participants:
                if not isinstance(participant, dict):
                    continue
                participant_family = str(participant.get("participant_family") or "").strip()
                if not participant_family:
                    continue
                family_participants[participant_family].append(participant)

            for participant_family, family_rows in family_participants.items():
                sample = by_family[participant_family]
                sample["sample_size"] = int(sample["sample_size"]) + 1
                if any(
                    self._is_direction_correct(
                        participant=participant,
                        actual_scenario=outcome.dominant_scenario_actual,
                    )
                    for participant in family_rows
                ):
                    sample["direction_correct"] = float(sample["direction_correct"]) + 1.0
                if any(str(participant.get("participant_id") or "") in early_detection_ids for participant in family_rows):
                    sample["early_detection"] = float(sample["early_detection"]) + 1.0
                if any(str(participant.get("participant_id") or "") in invalidation_ids for participant in family_rows):
                    sample["invalidation_detection"] = float(sample["invalidation_detection"]) + 1.0
                sample["last_score_label"] = outcome.score_label

        participants: list[ParticipantReliability] = []
        for participant_family, aggregate in by_family.items():
            sample_size = int(aggregate["sample_size"])
            low_sample_size = sample_size < 2
            direction_correct_score = self._ratio(float(aggregate["direction_correct"]), sample_size)
            early_detection_score = self._ratio(float(aggregate["early_detection"]), sample_size)
            invalidation_detection_score = self._ratio(float(aggregate["invalidation_detection"]), sample_size)
            participants.append(
                ParticipantReliability(
                    participant_family=participant_family,
                    sample_size=sample_size,
                    direction_correct_score=direction_correct_score,
                    early_detection_score=early_detection_score,
                    invalidation_detection_score=invalidation_detection_score,
                    last_score_label=str(aggregate["last_score_label"] or ""),
                    ability_tags=self._ability_tags(
                        direction_correct_score=direction_correct_score,
                        early_detection_score=early_detection_score,
                        invalidation_detection_score=invalidation_detection_score,
                    ),
                    low_sample_size=low_sample_size,
                )
            )
        participants.sort(
            key=lambda item: (
                -item.direction_correct_score,
                -item.early_detection_score,
                item.participant_family,
            )
        )
        status = "ready" if any(not item.low_sample_size for item in participants) else "low_sample_size"
        if not participants:
            status = "insufficient_evidence"
        return ReliabilitySummary(
            event_id=event_id,
            event_type=event_type,
            status=status,
            participants=participants,
        )

    def _persist_outcome(self, outcome: OutcomeReview) -> None:
        target_path = self.outcomes_root / f"{outcome.event_id}-{outcome.horizon}.json"
        target_path.write_text(json.dumps(asdict(outcome), ensure_ascii=False, indent=2), encoding="utf-8")

    def _iter_event_type_outcomes(self, event_type: str) -> list[OutcomeReview]:
        latest_by_event: dict[str, OutcomeReview] = {}
        for path in sorted(self.outcomes_root.glob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            outcome = OutcomeReview(**payload)
            if outcome.event_type != event_type:
                continue
            current = latest_by_event.get(outcome.event_id)
            if current is None or _HORIZON_ORDER.get(outcome.horizon, 0) >= _HORIZON_ORDER.get(current.horizon, 0):
                latest_by_event[outcome.event_id] = outcome
        return list(latest_by_event.values())

    def _normalize_horizon(self, horizon: str) -> str:
        normalized = str(horizon or "").strip().lower()
        if normalized not in _HORIZON_ORDER:
            raise OutcomeReviewError(
                code="OUTCOME_HORIZON_INVALID",
                message="Outcome horizon must be one of: t1, t3.",
                status_code=400,
            )
        return normalized

    def _derive_actual_scenario(
        self,
        *,
        sector_performance: str,
        leader_performance: str,
        expansion_status: str,
        sentiment_status: str,
    ) -> str:
        labels = [
            self._classify_signal(sector_performance),
            self._classify_signal(leader_performance),
            self._classify_signal(expansion_status),
            self._classify_signal(sentiment_status),
        ]
        positive_count = labels.count("positive")
        negative_count = labels.count("negative")
        mixed_count = labels.count("mixed")
        if mixed_count >= 2 or (positive_count >= 1 and negative_count >= 1):
            return "mixed"
        if positive_count >= 3:
            return "bull"
        if negative_count >= 3:
            return "bear"
        if positive_count >= 1 or negative_count >= 1:
            return "base"
        return "unclear"

    def _derive_score_label(
        self,
        *,
        predicted_scenario: str,
        actual_scenario: str,
        horizon: str,
        failure_reasons: list[str],
    ) -> str:
        if actual_scenario == "unclear":
            return "pending"
        if actual_scenario == predicted_scenario:
            return "hit"
        if actual_scenario == "mixed":
            return "partial_hit"
        if predicted_scenario == "base" and actual_scenario in {"bull", "bear"}:
            return "partial_hit"
        if predicted_scenario in {"bull", "bear"} and actual_scenario == "base":
            return "delayed_realization" if horizon == "t1" else "invalidated"
        if {predicted_scenario, actual_scenario} == {"bull", "bear"}:
            return "wrong_direction"
        if failure_reasons:
            return "invalidated"
        return "partial_hit"

    def _collect_failure_reasons(
        self,
        *,
        predicted_scenario: str,
        actual_scenario: str,
        sector_performance: str,
        leader_performance: str,
        expansion_status: str,
        sentiment_status: str,
    ) -> list[str]:
        reasons: list[str] = []
        signal_pairs = {
            "sector_underperformed": sector_performance,
            "leader_underperformed": leader_performance,
            "breadth_failed": expansion_status,
            "sentiment_rejected": sentiment_status,
        }
        for reason_code, value in signal_pairs.items():
            if self._classify_signal(value) == "negative":
                reasons.append(reason_code)
        if actual_scenario == "mixed":
            reasons.append("mixed_resolution")
        if predicted_scenario and actual_scenario and predicted_scenario != actual_scenario:
            reasons.append(f"predicted_{predicted_scenario}_actual_{actual_scenario}")
        return reasons

    def _collect_supporting_evidence(
        self,
        *,
        payload: OutcomeReviewWriteRequest,
        predicted_scenario: str,
        actual_scenario: str,
    ) -> list[str]:
        evidence = [
            f"predicted:{predicted_scenario}",
            f"actual:{actual_scenario}",
            f"sector:{payload.sector_performance}",
            f"leader:{payload.leader_performance}",
            f"expansion:{payload.expansion_status}",
            f"sentiment:{payload.sentiment_status}",
        ]
        for item in payload.supporting_evidence:
            normalized = str(item).strip()
            if normalized:
                evidence.append(normalized)
        return evidence

    def _classify_signal(self, value: str) -> str:
        normalized = str(value or "").strip().lower()
        if normalized in _POSITIVE_SIGNALS:
            return "positive"
        if normalized in _NEGATIVE_SIGNALS:
            return "negative"
        if normalized in {"mixed", "partial"}:
            return "mixed"
        return "neutral"

    def _extract_detection_ids(self, run: dict[str, object]) -> tuple[set[str], set[str]]:
        early_detection_ids: set[str] = set()
        invalidation_ids: set[str] = set()
        round_results = run.get("round_results") if isinstance(run.get("round_results"), list) else []
        for round_result in round_results:
            if not isinstance(round_result, dict):
                continue
            order = int(round_result.get("order") or 0)
            updates = round_result.get("participant_updates") if isinstance(round_result.get("participant_updates"), list) else []
            for update in updates:
                if not isinstance(update, dict):
                    continue
                participant_id = str(update.get("participant_id") or "")
                action_name = str(update.get("action_name") or "")
                if order <= 2 and action_name in {"INIT_BUY", "ADD_BUY", "BROADCAST_BULL"}:
                    early_detection_ids.add(participant_id)
                if action_name in {"REDUCE", "EXIT", "BROADCAST_BEAR"}:
                    invalidation_ids.add(participant_id)
        return early_detection_ids, invalidation_ids

    def _is_direction_correct(self, *, participant: dict[str, object], actual_scenario: str) -> bool:
        stance = str(participant.get("stance") or "").strip().lower()
        role = str(participant.get("role") or "").strip().lower()
        if actual_scenario == "bull":
            return stance in _SUPPORTIVE_STANCES or role in {"leader", "follower", "amplifier"}
        if actual_scenario == "bear":
            return stance in _DEFENSIVE_STANCES or role == "risk_guard"
        if actual_scenario == "base":
            return stance in {"neutral", "watch"} or role == "risk_guard"
        return stance in {"watch", "neutral"} or role == "risk_guard"

    def _ability_tags(
        self,
        *,
        direction_correct_score: float,
        early_detection_score: float,
        invalidation_detection_score: float,
    ) -> list[str]:
        ability_tags: list[str] = []
        if direction_correct_score >= 0.5:
            ability_tags.append("direction_correct")
        if early_detection_score >= 0.5:
            ability_tags.append("early_detection")
        if invalidation_detection_score >= 0.5:
            ability_tags.append("invalidation_detection")
        return ability_tags

    def _ratio(self, numerator: float, denominator: int) -> float:
        if denominator <= 0:
            return 0.0
        return round(numerator / denominator, 2)

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

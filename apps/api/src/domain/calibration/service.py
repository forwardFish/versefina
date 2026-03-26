from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path

from domain.mirror_agent.service import MirrorAgentService
from domain.participant_preparation.registry import ParticipantRegistry
from domain.scenario_engine.service import ScenarioEngineService
from schemas.calibration import (
    BeliefPatternStat,
    CalibrationFeedback,
    DistributionCalibrationSummary,
    ParticipantSegmentStat,
    ParticipantWeightRecommendation,
    ScenarioWeightRecommendation,
)


class CalibrationService:
    def __init__(
        self,
        *,
        style_root: Path,
        mirror_agent_service: MirrorAgentService,
        participant_registry: ParticipantRegistry,
        scenario_engine: ScenarioEngineService,
    ) -> None:
        self.style_root = style_root
        self.mirror_agent_service = mirror_agent_service
        self.participant_registry = participant_registry
        self.scenario_engine = scenario_engine
        self.distribution_root = style_root / "distribution_calibration"
        self.feedback_root = style_root / "weight_feedback"
        self.distribution_root.mkdir(parents=True, exist_ok=True)
        self.feedback_root.mkdir(parents=True, exist_ok=True)

    def build_distribution_calibration(self, statement_id: str) -> DistributionCalibrationSummary:
        mirror_agent = self.mirror_agent_service.load_mirror_agent(statement_id) or self.mirror_agent_service.build_mirror_agent(statement_id)
        validation = self.mirror_agent_service.load_mirror_validation(statement_id) or self.mirror_agent_service.validate_mirror_agent(statement_id)
        rules = list((mirror_agent.activation_calibration or {}).get("rules") or [])
        sample_size = 1 if validation.provisional else 3
        participant_segments = [
            ParticipantSegmentStat(
                event_type=str(rule.get("event_type") or "supply_chain_price_shock"),
                participant_family=str(rule.get("participant_family") or mirror_agent.participant_family),
                sample_size=sample_size,
                hit_rate=round(float(rule.get("activation_weight") or 0.0), 2),
                failure_rate=round(1 - float(rule.get("activation_weight") or 0.0), 2),
                insufficient_sample=validation.provisional,
            )
            for rule in rules
        ]
        belief_patterns = [
            BeliefPatternStat(
                pattern="momentum_follow_through",
                hit_count=1 if float((mirror_agent.style_embedding or {}).get("momentum_preference_score") or 0.0) >= 0.6 else 0,
                failure_count=1 if validation.noise == "high_noise" else 0,
            ),
            BeliefPatternStat(
                pattern="defensive_invalidation",
                hit_count=1 if validation.risk == "guarded" else 0,
                failure_count=1 if validation.risk == "aggressive" else 0,
            ),
        ]
        summary = DistributionCalibrationSummary(
            statement_id=statement_id,
            status="partial" if validation.provisional else "ready",
            participant_segments=participant_segments,
            belief_patterns=belief_patterns,
            source_validation=validation.to_dict(),
        )
        self._persist(self.distribution_root, statement_id, asdict(summary))
        return summary

    def load_distribution_calibration(self, statement_id: str) -> DistributionCalibrationSummary | None:
        payload = self._load_payload(self.distribution_root, statement_id)
        if payload is None:
            return None
        payload["participant_segments"] = [ParticipantSegmentStat(**item) for item in payload.get("participant_segments", [])]
        payload["belief_patterns"] = [BeliefPatternStat(**item) for item in payload.get("belief_patterns", [])]
        return DistributionCalibrationSummary(**payload)

    def build_weight_feedback(self, statement_id: str) -> CalibrationFeedback:
        summary = self.load_distribution_calibration(statement_id) or self.build_distribution_calibration(statement_id)
        apply_allowed = not any(item.insufficient_sample for item in summary.participant_segments)
        participant_weight_payload = [
            {
                "participant_family": item.participant_family,
                "suggested_weight": round(min(0.95, 0.35 + item.hit_rate * 0.6), 2),
                "reason": f"{item.event_type} calibration derived from hit_rate {item.hit_rate:.2f}.",
            }
            for item in summary.participant_segments
        ]
        participant_preview = self.participant_registry.preview_weight_feedback(participant_weight_payload)
        scenario_preview = self.scenario_engine.preview_weight_feedback(
            [
                {
                    "scenario_id": "bull",
                    "suggested_weight": 0.6 if not summary.source_validation.get("provisional") else 0.45,
                    "reason": "Bull weight follows the style mirror validation profile.",
                },
                {
                    "scenario_id": "bear",
                    "suggested_weight": 0.4 if summary.source_validation.get("risk") != "aggressive" else 0.55,
                    "reason": "Bear weight remains elevated when validation risk is aggressive.",
                },
            ]
        )
        feedback = CalibrationFeedback(
            statement_id=statement_id,
            status="partial" if not apply_allowed else "ready",
            apply_allowed=apply_allowed,
            participant_weights=[ParticipantWeightRecommendation(**item) for item in participant_preview],
            scenario_weights=[ScenarioWeightRecommendation(**item) for item in scenario_preview],
            review_required=True,
        )
        self._persist(self.feedback_root, statement_id, asdict(feedback))
        return feedback

    def load_weight_feedback(self, statement_id: str) -> CalibrationFeedback | None:
        payload = self._load_payload(self.feedback_root, statement_id)
        if payload is None:
            return None
        payload["participant_weights"] = [ParticipantWeightRecommendation(**item) for item in payload.get("participant_weights", [])]
        payload["scenario_weights"] = [ScenarioWeightRecommendation(**item) for item in payload.get("scenario_weights", [])]
        return CalibrationFeedback(**payload)

    def _persist(self, root: Path, statement_id: str, payload: dict[str, object]) -> None:
        target_path = root / f"{statement_id}.json"
        target_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _load_payload(self, root: Path, statement_id: str) -> dict[str, object] | None:
        target_path = root / f"{statement_id}.json"
        if not target_path.exists():
            return None
        return json.loads(target_path.read_text(encoding="utf-8"))

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from schemas.e2_005 import ParticipantRegistryEntry, ParticipantRegistrySnapshot


@dataclass(frozen=True, slots=True)
class ParticipantVariantDefinition:
    participant_family: str
    style_variant: str
    authority_weight: float
    risk_budget_profile: str
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


PRIMARY_VARIANTS = (
    ParticipantVariantDefinition("retail_fast_money", "fast_momentum", 0.62, "high_turnover", ["first mover"]),
    ParticipantVariantDefinition("institution_confirmation", "trend_confirmation", 0.78, "risk_adjusted_add", ["follow through"]),
    ParticipantVariantDefinition("industry_research", "fundamental_channel_check", 0.74, "medium_conviction", ["supply chain verification"]),
    ParticipantVariantDefinition("policy_research", "policy_interpretation", 0.68, "theme_rotation", ["policy impulse"]),
    ParticipantVariantDefinition("quant_risk_budget", "factor_rotation", 0.57, "model_capped", ["flow driven"]),
    ParticipantVariantDefinition("risk_control", "drawdown_guard", 0.83, "capital_preservation", ["invalidation first"]),
    ParticipantVariantDefinition("media_sentiment", "headline_amplifier", 0.51, "event_reactive", ["sentiment spread"]),
    ParticipantVariantDefinition("supply_chain_channel", "channel_pass_through", 0.76, "inventory_sensitive", ["industrial chain"]),
)


class ParticipantRegistry:
    def __init__(self) -> None:
        self._primary_variants = {item.participant_family: item for item in PRIMARY_VARIANTS}

    def list_primary_variants(self) -> list[ParticipantVariantDefinition]:
        return list(self._primary_variants.values())

    def get_primary_variant(self, participant_family: str) -> ParticipantVariantDefinition | None:
        return self._primary_variants.get(participant_family)

    def list_registry_entries(self) -> list[ParticipantRegistryEntry]:
        return [
            ParticipantRegistryEntry(
                participant_family=item.participant_family,
                style_variant=item.style_variant,
                authority_weight=item.authority_weight,
                risk_budget_profile=item.risk_budget_profile,
                notes=list(item.notes),
                calibration_status="default",
            )
            for item in self.list_primary_variants()
        ]

    def get_registry_entry(self, participant_family: str) -> ParticipantRegistryEntry | None:
        variant = self.get_primary_variant(participant_family)
        if variant is None:
            return None
        return ParticipantRegistryEntry(
            participant_family=variant.participant_family,
            style_variant=variant.style_variant,
            authority_weight=variant.authority_weight,
            risk_budget_profile=variant.risk_budget_profile,
            notes=list(variant.notes),
            calibration_status="default",
        )

    def preview_weight_feedback(self, recommendations: list[dict[str, object]]) -> list[dict[str, object]]:
        preview: list[dict[str, object]] = []
        for recommendation in recommendations:
            participant_family = str(recommendation.get("participant_family") or "")
            current = self.get_primary_variant(participant_family)
            current_weight = current.authority_weight if current is not None else 0.5
            preview.append(
                {
                    "participant_family": participant_family,
                    "current_weight": round(current_weight, 2),
                    "suggested_weight": round(float(recommendation.get("suggested_weight") or current_weight), 2),
                    "reason": str(recommendation.get("reason") or ""),
                }
            )
        return preview

    def snapshot(self) -> ParticipantRegistrySnapshot:
        return ParticipantRegistrySnapshot(entries=self.list_registry_entries())

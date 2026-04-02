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
    clone_index: int = 0
    influence_weight: float = 0.0
    capital_bucket: str = ""
    capital_base: float = 0.0
    max_event_exposure: float = 0.0
    seed_position_ratio: float = 0.0
    reaction_latency: int = 0
    entry_threshold: float = 0.0
    add_threshold: float = 0.0
    reduce_threshold: float = 0.0
    exit_threshold: float = 0.0
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


PRIMARY_VARIANTS = (
    ParticipantVariantDefinition(
        "retail_fast_money",
        "fast_momentum",
        0.62,
        "high_turnover",
        clone_index=1,
        influence_weight=0.63,
        capital_bucket="retail_small",
        capital_base=4_000_000,
        max_event_exposure=0.32,
        reaction_latency=0,
        entry_threshold=0.56,
        add_threshold=0.68,
        reduce_threshold=0.54,
        exit_threshold=0.7,
        notes=["first mover"],
    ),
    ParticipantVariantDefinition(
        "institution_confirmation",
        "trend_confirmation",
        0.78,
        "risk_adjusted_add",
        clone_index=1,
        influence_weight=0.78,
        capital_bucket="institution_mid",
        capital_base=80_000_000,
        max_event_exposure=0.18,
        seed_position_ratio=0.04,
        reaction_latency=1,
        entry_threshold=0.62,
        add_threshold=0.71,
        reduce_threshold=0.57,
        exit_threshold=0.74,
        notes=["follow through"],
    ),
    ParticipantVariantDefinition(
        "industry_research",
        "fundamental_channel_check",
        0.74,
        "medium_conviction",
        clone_index=1,
        influence_weight=0.71,
        capital_bucket="specialist_research",
        capital_base=36_000_000,
        max_event_exposure=0.2,
        reaction_latency=1,
        entry_threshold=0.58,
        add_threshold=0.69,
        reduce_threshold=0.53,
        exit_threshold=0.72,
        notes=["supply chain verification"],
    ),
    ParticipantVariantDefinition(
        "policy_research",
        "policy_interpretation",
        0.68,
        "theme_rotation",
        clone_index=1,
        influence_weight=0.59,
        capital_bucket="policy_fund",
        capital_base=28_000_000,
        max_event_exposure=0.16,
        reaction_latency=2,
        entry_threshold=0.64,
        add_threshold=0.74,
        reduce_threshold=0.52,
        exit_threshold=0.69,
        notes=["policy impulse"],
    ),
    ParticipantVariantDefinition(
        "quant_risk_budget",
        "factor_rotation",
        0.57,
        "model_capped",
        clone_index=1,
        influence_weight=0.52,
        capital_bucket="quant_pool",
        capital_base=32_000_000,
        max_event_exposure=0.14,
        reaction_latency=1,
        entry_threshold=0.6,
        add_threshold=0.7,
        reduce_threshold=0.55,
        exit_threshold=0.71,
        notes=["flow driven"],
    ),
    ParticipantVariantDefinition(
        "risk_control",
        "drawdown_guard",
        0.83,
        "capital_preservation",
        clone_index=1,
        influence_weight=0.81,
        capital_bucket="risk_overlay",
        capital_base=24_000_000,
        max_event_exposure=0.08,
        reaction_latency=0,
        entry_threshold=0.75,
        add_threshold=0.82,
        reduce_threshold=0.46,
        exit_threshold=0.58,
        notes=["invalidation first"],
    ),
    ParticipantVariantDefinition(
        "media_sentiment",
        "headline_amplifier",
        0.51,
        "event_reactive",
        clone_index=1,
        influence_weight=0.67,
        capital_bucket="sentiment_desk",
        capital_base=6_500_000,
        max_event_exposure=0.11,
        reaction_latency=0,
        entry_threshold=0.59,
        add_threshold=0.71,
        reduce_threshold=0.56,
        exit_threshold=0.73,
        notes=["sentiment spread"],
    ),
    ParticipantVariantDefinition(
        "supply_chain_channel",
        "channel_pass_through",
        0.76,
        "inventory_sensitive",
        clone_index=1,
        influence_weight=0.74,
        capital_bucket="channel_network",
        capital_base=42_000_000,
        max_event_exposure=0.2,
        seed_position_ratio=0.03,
        reaction_latency=0,
        entry_threshold=0.55,
        add_threshold=0.67,
        reduce_threshold=0.5,
        exit_threshold=0.68,
        notes=["industrial chain"],
    ),
)

CLONE_VARIANTS = (
    ParticipantVariantDefinition("retail_fast_money", "fast_momentum", 0.62, "high_turnover", 1, 0.63, "retail_small", 4_000_000, 0.32, 0.0, 0, 0.56, 0.68, 0.54, 0.7, ["first mover"]),
    ParticipantVariantDefinition("retail_fast_money", "gap_chaser", 0.58, "high_turnover", 2, 0.58, "retail_small", 3_200_000, 0.29, 0.0, 0, 0.58, 0.69, 0.55, 0.72, ["breakout watch"]),
    ParticipantVariantDefinition("retail_fast_money", "late_rotation", 0.52, "swing_chase", 3, 0.49, "retail_mid", 2_400_000, 0.24, 0.0, 1, 0.62, 0.72, 0.52, 0.68, ["follows visible breadth"]),
    ParticipantVariantDefinition("retail_fast_money", "crowd_scalper", 0.47, "headline_reactive", 4, 0.46, "retail_micro", 1_600_000, 0.22, 0.0, 1, 0.64, 0.74, 0.5, 0.66, ["sensitive to sentiment"]),
    ParticipantVariantDefinition("institution_confirmation", "trend_confirmation", 0.78, "risk_adjusted_add", 1, 0.78, "institution_mid", 80_000_000, 0.18, 0.04, 1, 0.62, 0.71, 0.57, 0.74, ["follow through"]),
    ParticipantVariantDefinition("institution_confirmation", "liquidity_allocator", 0.82, "risk_adjusted_add", 2, 0.8, "institution_large", 120_000_000, 0.16, 0.06, 1, 0.63, 0.72, 0.58, 0.75, ["needs leadership confirmation"]),
    ParticipantVariantDefinition("institution_confirmation", "relative_strength_pm", 0.75, "sector_relative", 3, 0.73, "institution_mid", 68_000_000, 0.17, 0.02, 2, 0.65, 0.73, 0.56, 0.73, ["adds after breadth"]),
    ParticipantVariantDefinition("industry_research", "fundamental_channel_check", 0.74, "medium_conviction", 1, 0.71, "specialist_research", 36_000_000, 0.2, 0.0, 1, 0.58, 0.69, 0.53, 0.72, ["supply chain verification"]),
    ParticipantVariantDefinition("industry_research", "cost_curve_specialist", 0.79, "deep_dive", 2, 0.76, "specialist_research", 44_000_000, 0.18, 0.03, 1, 0.57, 0.67, 0.52, 0.7, ["high authority on pass-through"]),
    ParticipantVariantDefinition("industry_research", "inventory_mapper", 0.69, "medium_conviction", 3, 0.65, "specialist_research", 30_000_000, 0.17, 0.0, 2, 0.61, 0.71, 0.51, 0.69, ["waits for channel checks"]),
    ParticipantVariantDefinition("policy_research", "policy_interpretation", 0.68, "theme_rotation", 1, 0.59, "policy_fund", 28_000_000, 0.16, 0.0, 2, 0.64, 0.74, 0.52, 0.69, ["policy impulse"]),
    ParticipantVariantDefinition("policy_research", "macro_rotation", 0.64, "theme_rotation", 2, 0.56, "policy_fund", 24_000_000, 0.14, 0.0, 2, 0.66, 0.75, 0.51, 0.68, ["cares about official reinforcement"]),
    ParticipantVariantDefinition("quant_risk_budget", "factor_rotation", 0.57, "model_capped", 1, 0.52, "quant_pool", 32_000_000, 0.14, 0.0, 1, 0.6, 0.7, 0.55, 0.71, ["flow driven"]),
    ParticipantVariantDefinition("quant_risk_budget", "breadth_model", 0.61, "model_capped", 2, 0.55, "quant_pool", 40_000_000, 0.13, 0.0, 2, 0.62, 0.71, 0.54, 0.7, ["requires breadth expansion"]),
    ParticipantVariantDefinition("risk_control", "drawdown_guard", 0.83, "capital_preservation", 1, 0.81, "risk_overlay", 24_000_000, 0.08, 0.01, 0, 0.75, 0.82, 0.46, 0.58, ["invalidation first"]),
    ParticipantVariantDefinition("risk_control", "exposure_governor", 0.8, "capital_preservation", 2, 0.79, "risk_overlay", 26_000_000, 0.07, 0.0, 0, 0.77, 0.84, 0.44, 0.56, ["cuts crowded trades first"]),
    ParticipantVariantDefinition("media_sentiment", "headline_amplifier", 0.51, "event_reactive", 1, 0.67, "sentiment_desk", 6_500_000, 0.11, 0.0, 0, 0.59, 0.71, 0.56, 0.73, ["sentiment spread"]),
    ParticipantVariantDefinition("media_sentiment", "social_feed_router", 0.48, "event_reactive", 2, 0.64, "sentiment_desk", 5_200_000, 0.1, 0.0, 0, 0.6, 0.72, 0.55, 0.72, ["broadcasts crowd tone"]),
    ParticipantVariantDefinition("supply_chain_channel", "channel_pass_through", 0.76, "inventory_sensitive", 1, 0.74, "channel_network", 42_000_000, 0.2, 0.03, 0, 0.55, 0.67, 0.5, 0.68, ["industrial chain"]),
    ParticipantVariantDefinition("supply_chain_channel", "spot_inventory_router", 0.72, "inventory_sensitive", 2, 0.7, "channel_network", 34_000_000, 0.18, 0.02, 1, 0.57, 0.68, 0.5, 0.67, ["tracks spot inventory"]),
)


class ParticipantRegistry:
    def __init__(self) -> None:
        self._primary_variants = {item.participant_family: item for item in PRIMARY_VARIANTS}
        self._clone_variants = list(CLONE_VARIANTS)

    def list_primary_variants(self) -> list[ParticipantVariantDefinition]:
        return list(self._primary_variants.values())

    def get_primary_variant(self, participant_family: str) -> ParticipantVariantDefinition | None:
        return self._primary_variants.get(participant_family)

    def list_clone_variants(self) -> list[ParticipantVariantDefinition]:
        return list(self._clone_variants)

    def list_registry_entries(self) -> list[ParticipantRegistryEntry]:
        return [
            self._to_registry_entry(item)
            for item in self.list_primary_variants()
        ]

    def get_registry_entry(self, participant_family: str) -> ParticipantRegistryEntry | None:
        variant = self.get_primary_variant(participant_family)
        if variant is None:
            return None
        return self._to_registry_entry(variant)

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

    def _to_registry_entry(self, variant: ParticipantVariantDefinition) -> ParticipantRegistryEntry:
        return ParticipantRegistryEntry(
            participant_family=variant.participant_family,
            style_variant=variant.style_variant,
            authority_weight=variant.authority_weight,
            risk_budget_profile=variant.risk_budget_profile,
            influence_weight=variant.influence_weight,
            capital_bucket=variant.capital_bucket,
            capital_base=variant.capital_base,
            max_event_exposure=variant.max_event_exposure,
            reaction_latency=variant.reaction_latency,
            entry_threshold=variant.entry_threshold,
            add_threshold=variant.add_threshold,
            reduce_threshold=variant.reduce_threshold,
            exit_threshold=variant.exit_threshold,
            notes=list(variant.notes),
            calibration_status="default",
        )

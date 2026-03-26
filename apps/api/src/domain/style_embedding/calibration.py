from __future__ import annotations

from schemas.style import ArchetypeSeed, ParticipantActivationCalibration, ParticipantActivationRule

_CALIBRATION_LIBRARY: dict[str, list[tuple[str, str, float, str]]] = {
    "retail_fast_money": [
        (
            "supply_chain_price_shock",
            "retail_fast_money",
            0.85,
            "Fast-money participants should react first when a price shock broadens quickly.",
        ),
        (
            "supply_chain_price_shock",
            "media_sentiment",
            0.7,
            "Headline amplification tends to reinforce the same momentum regime.",
        ),
    ],
    "institution_confirmation": [
        (
            "supply_chain_price_shock",
            "institution_confirmation",
            0.8,
            "Institutional confirmation activates after first movers validate sector leadership.",
        ),
        (
            "supply_chain_price_shock",
            "supply_chain_channel",
            0.68,
            "Channel checks help confirm whether the move is grounded in real pass-through.",
        ),
    ],
    "industry_research": [
        (
            "supply_chain_price_shock",
            "industry_research",
            0.76,
            "Industry research should activate when style signals imply slower but deeper follow-through.",
        ),
    ],
    "quant_risk_budget": [
        (
            "supply_chain_price_shock",
            "quant_risk_budget",
            0.62,
            "Balanced style profiles should default to risk-budgeted activation until the signal strengthens.",
        ),
    ],
}


def build_activation_calibration(seed: ArchetypeSeed) -> ParticipantActivationCalibration:
    descriptors = _CALIBRATION_LIBRARY.get(seed.participant_family)
    if not descriptors:
        return ParticipantActivationCalibration(
            statement_id=seed.statement_id,
            status="default_activation",
            source_archetype=seed.archetype_name,
            default_activation=True,
            rules=[
                ParticipantActivationRule(
                    event_type="supply_chain_price_shock",
                    participant_family=seed.participant_family,
                    activation_weight=0.4,
                    reason="Default activation because no dedicated calibration rule matched the seed.",
                )
            ],
        )
    return ParticipantActivationCalibration(
        statement_id=seed.statement_id,
        status="ready" if not seed.low_confidence else "partial",
        source_archetype=seed.archetype_name,
        default_activation=False,
        rules=[
            ParticipantActivationRule(
                event_type=event_type,
                participant_family=participant_family,
                activation_weight=activation_weight,
                reason=reason,
            )
            for event_type, participant_family, activation_weight, reason in descriptors
        ],
    )

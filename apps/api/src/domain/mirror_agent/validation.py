from __future__ import annotations

from schemas.mirror_agent import MirrorAgent, MirrorAgentValidation


def validate_mirror_agent(agent: MirrorAgent) -> MirrorAgentValidation:
    style_embedding = dict(agent.style_embedding or {})
    concentration_score = float(style_embedding.get("concentration_score") or 0.0)
    low_confidence = bool(style_embedding.get("low_confidence"))
    latency_label = str((style_embedding.get("reaction_latency_profile") or {}).get("label") or "medium")
    momentum_score = float(style_embedding.get("momentum_preference_score") or 0.0)

    if concentration_score >= 0.65:
        risk = "aggressive"
    elif concentration_score >= 0.4:
        risk = "balanced"
    else:
        risk = "guarded"

    noise = "high_noise" if low_confidence or 0.45 <= momentum_score <= 0.55 else "low_noise"
    hold = "short_hold" if latency_label == "fast" else "swing_hold" if latency_label == "medium" else "position_hold"

    reasons: list[str] = []
    if low_confidence:
        reasons.append("style_signal_provisional")
    if noise == "high_noise":
        reasons.append("signal_noise_high")
    if risk == "aggressive":
        reasons.append("concentration_above_guardrail")

    if low_confidence:
        grading = "provisional"
    elif risk == "balanced" and noise == "low_noise":
        grading = "A"
    elif risk in {"balanced", "guarded"}:
        grading = "B"
    else:
        grading = "C"

    return MirrorAgentValidation(
        statement_id=agent.statement_id,
        status="partial" if low_confidence else "ready",
        risk=risk,
        noise=noise,
        hold=hold,
        grading=grading,
        provisional=low_confidence,
        reasons=reasons,
    )

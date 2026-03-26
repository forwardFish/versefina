from __future__ import annotations

from domain.event_casebook.service import EventCasebookService
from domain.participant_preparation.registry import ParticipantRegistry
from schemas.command import EventPrepareResponse
from schemas.participant import ParticipantOutput
from schemas.participant_preparation import ParticipantRoster
from schemas.simulation import SIMULATION_ACTION_PROTOCOL


_FAMILY_PLAYBOOK: dict[str, dict[str, str]] = {
    "retail_fast_money": {
        "stance": "bullish",
        "time_horizon": "intraday",
        "impact": "leads the first momentum chase",
        "reason": "spot price breakout is visible to fast-money desks",
    },
    "institution_confirmation": {
        "stance": "constructive",
        "time_horizon": "t1",
        "impact": "confirms the strongest first-mover names",
        "reason": "needs confirmation from sector leadership and liquidity follow-through",
    },
    "industry_research": {
        "stance": "constructive",
        "time_horizon": "t3",
        "impact": "checks whether the industrial chain can pass through costs",
        "reason": "validates channel and supply-chain transmission",
    },
    "policy_research": {
        "stance": "watch",
        "time_horizon": "t3",
        "impact": "looks for policy reinforcement or offsetting guidance",
        "reason": "monitors whether policy direction amplifies the theme",
    },
    "quant_risk_budget": {
        "stance": "neutral",
        "time_horizon": "t1",
        "impact": "sizes exposure only when factor breadth confirms",
        "reason": "waits for volatility and factor confirmation",
    },
    "risk_control": {
        "stance": "watch",
        "time_horizon": "intraday",
        "impact": "guards the invalidation line before capital is committed",
        "reason": "tracks drawdown and reversal pressure first",
    },
    "media_sentiment": {
        "stance": "constructive",
        "time_horizon": "intraday",
        "impact": "amplifies the headline into broader crowd attention",
        "reason": "headline velocity can widen the participation set",
    },
    "supply_chain_channel": {
        "stance": "constructive",
        "time_horizon": "t1",
        "impact": "tests inventory and pricing pass-through on the ground",
        "reason": "channel checks validate whether the signal is real",
    },
}

_DEFAULT_ACTIONS = tuple(SIMULATION_ACTION_PROTOCOL)
_FAMILY_INITIAL_STATES: dict[str, str] = {
    "retail_fast_money": "ready",
    "institution_confirmation": "watching",
    "industry_research": "validated",
    "policy_research": "watching",
    "quant_risk_budget": "watching",
    "risk_control": "watching",
    "media_sentiment": "ready",
    "supply_chain_channel": "validated",
}
_FAMILY_ALLOWED_ACTIONS: dict[str, tuple[str, ...]] = {
    "retail_fast_money": ("WATCH", "VALIDATE", "LEAD", "BROADCAST_BULL", "FOLLOW", "EXIT"),
    "institution_confirmation": ("WATCH", "VALIDATE", "FOLLOW", "BROADCAST_BULL", "EXIT"),
    "industry_research": ("IGNORE", "WATCH", "VALIDATE", "BROADCAST_BULL", "BROADCAST_BEAR", "FOLLOW", "EXIT"),
    "policy_research": ("IGNORE", "WATCH", "VALIDATE", "FOLLOW", "EXIT"),
    "quant_risk_budget": ("IGNORE", "WATCH", "VALIDATE", "FOLLOW", "EXIT"),
    "risk_control": ("IGNORE", "WATCH", "VALIDATE", "BROADCAST_BEAR", "EXIT"),
    "media_sentiment": ("WATCH", "VALIDATE", "BROADCAST_BULL", "BROADCAST_BEAR", "FOLLOW", "EXIT"),
    "supply_chain_channel": ("WATCH", "VALIDATE", "LEAD", "FOLLOW", "EXIT"),
}


class ParticipantPreparationError(Exception):
    def __init__(self, *, code: str, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class ParticipantPreparationService:
    def __init__(self, casebook_service: EventCasebookService, participant_registry: ParticipantRegistry) -> None:
        self.casebook_service = casebook_service
        self.participant_registry = participant_registry

    def prepare_event(self, event_id: str) -> EventPrepareResponse:
        casebook = self.casebook_service.load_casebook(event_id)
        if casebook is None:
            raise ParticipantPreparationError(
                code="EVENT_NOT_FOUND",
                message="Event casebook not found.",
                status_code=404,
            )

        blocked_reasons = self._collect_blocked_reasons(casebook.structure, casebook.mapping)
        activation_basis = self._build_activation_basis(casebook.structure, casebook.mapping)
        if blocked_reasons:
            roster = ParticipantRoster(
                event_id=event_id,
                status="degraded",
                participants=[],
                blocked_reasons=blocked_reasons,
                activation_basis=activation_basis,
            )
            return EventPrepareResponse(
                event_id=event_id,
                status="degraded",
                casebook=casebook.to_dict(),
                participant_roster=roster.to_dict(),
            )

        prepared_casebook = self.casebook_service.mark_prepared(event_id)
        roster = ParticipantRoster(
            event_id=event_id,
            status="prepared",
            participants=self._build_participants(prepared_casebook.structure, prepared_casebook.mapping),
            blocked_reasons=[],
            activation_basis=activation_basis,
        )
        return EventPrepareResponse(
            event_id=event_id,
            status="prepared",
            casebook=prepared_casebook.to_dict(),
            participant_roster=roster.to_dict(),
        )

    def _collect_blocked_reasons(self, structure: dict[str, object], mapping: dict[str, object]) -> list[str]:
        blocked: list[str] = []
        if structure.get("event_type") != "supply_chain_price_shock":
            blocked.append("prepare currently supports supply_chain_price_shock events only")
        if not structure.get("commodities"):
            blocked.append("structured event is missing commodity evidence")
        symbol_candidates = mapping.get("symbols") or structure.get("affected_symbols")
        if not symbol_candidates:
            blocked.append("structured event is missing first-mover symbols")
        if not structure.get("monitor_signals"):
            blocked.append("structured event is missing monitor signals")
        return blocked

    def _build_activation_basis(self, structure: dict[str, object], mapping: dict[str, object]) -> list[str]:
        basis: list[str] = []
        summary = str(structure.get("summary") or "").strip()
        if summary:
            basis.append(summary)
        for signal in list(structure.get("monitor_signals") or [])[:2]:
            basis.append(f"monitor:{signal}")
        for symbol in list(mapping.get("symbols") or structure.get("affected_symbols") or [])[:2]:
            basis.append(f"symbol:{symbol}")
        sector = str(mapping.get("sector") or "").strip()
        if sector:
            basis.append(f"sector:{sector}")
        return basis

    def _build_participants(
        self,
        structure: dict[str, object],
        mapping: dict[str, object],
    ) -> list[ParticipantOutput]:
        participants: list[ParticipantOutput] = []
        first_movers = list(mapping.get("symbols") or structure.get("affected_symbols") or [])
        focus = str(mapping.get("commodity") or (list(structure.get("commodities") or ["event"])[0]))
        activation_basis = self._build_activation_basis(structure, mapping)
        trigger_conditions = list(structure.get("monitor_signals") or [])[:3]
        invalidation_conditions = list(structure.get("invalidation_conditions") or [])[:3]
        for variant in self.participant_registry.list_primary_variants():
            playbook = _FAMILY_PLAYBOOK.get(variant.participant_family, {})
            confidence = round(min(0.95, 0.35 + variant.authority_weight * 0.55), 2)
            participants.append(
                ParticipantOutput(
                    participant_id=f"{variant.participant_family}:{variant.style_variant}",
                    participant_family=variant.participant_family,
                    style_variant=variant.style_variant,
                    stance=playbook.get("stance", "neutral"),
                    confidence=confidence,
                    time_horizon=playbook.get("time_horizon", "t1"),
                    expected_impact=f"{playbook.get('impact', 'tracks the event')} around {focus}",
                    evidence=activation_basis[:3],
                    trigger_conditions=trigger_conditions,
                    invalidation_conditions=invalidation_conditions,
                    first_movers=first_movers[:2],
                    secondary_movers=first_movers[2:4],
                    dissent_points=list(variant.notes[:1]),
                    initial_state=self._initial_state_for(variant.participant_family),
                    allowed_actions=self._allowed_actions_for(variant.participant_family),
                    authority_weight=variant.authority_weight,
                    risk_budget_profile=variant.risk_budget_profile,
                )
            )
        return participants

    def _initial_state_for(self, participant_family: str) -> str:
        return _FAMILY_INITIAL_STATES.get(participant_family, "ready")

    def _allowed_actions_for(self, participant_family: str) -> list[str]:
        configured = _FAMILY_ALLOWED_ACTIONS.get(participant_family, _DEFAULT_ACTIONS)
        return [action for action in configured if action in SIMULATION_ACTION_PROTOCOL]

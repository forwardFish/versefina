from __future__ import annotations

from domain.participant_preparation.service import ParticipantPreparationError, ParticipantPreparationService
from schemas.belief_graph import BeliefGraphNode, BeliefGraphSnapshot


_SUPPORTIVE_STANCES = {"bullish", "constructive"}
_OPPOSING_STANCES = {"watch", "skeptical", "bearish"}


class BeliefGraphError(Exception):
    def __init__(self, *, code: str, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class BeliefGraphService:
    def __init__(self, participant_preparation: ParticipantPreparationService) -> None:
        self.participant_preparation = participant_preparation

    def build_snapshot(self, event_id: str) -> BeliefGraphSnapshot:
        try:
            prepare_result = self.participant_preparation.prepare_event(event_id)
        except ParticipantPreparationError as exc:
            raise BeliefGraphError(code=exc.code, message=exc.message, status_code=exc.status_code) from exc

        roster = dict(prepare_result.participant_roster or {})
        participants = list(roster.get("participants") or [])
        if not participants:
            return BeliefGraphSnapshot(
                event_id=event_id,
                status="empty",
                participant_count=0,
                key_supporters=[],
                key_opponents=[],
                consensus_signals=list(roster.get("blocked_reasons") or []),
                divergence_signals=[],
                nodes=[],
            )

        nodes = [
            BeliefGraphNode(
                participant_id=str(item.get("participant_id") or item.get("participant_family") or "unknown"),
                participant_family=str(item.get("participant_family") or "unknown"),
                stance=str(item.get("stance") or "neutral"),
                authority_weight=float(item.get("authority_weight") or 0.0),
                confidence=float(item.get("confidence") or 0.0),
            )
            for item in participants
        ]
        supporters = [
            node.participant_family
            for node in sorted(nodes, key=lambda item: (-item.authority_weight, -item.confidence))
            if node.stance in _SUPPORTIVE_STANCES
        ]
        opponents = [
            node.participant_family
            for node in sorted(nodes, key=lambda item: (-item.authority_weight, -item.confidence))
            if node.stance in _OPPOSING_STANCES
        ]
        consensus_signals = self._dedupe(
            signal
            for item in participants
            for signal in list(item.get("trigger_conditions") or [])[:2]
        )
        divergence_signals = self._dedupe(
            signal
            for item in participants
            for signal in list(item.get("invalidation_conditions") or [])[:2] + list(item.get("dissent_points") or [])[:1]
        )
        return BeliefGraphSnapshot(
            event_id=event_id,
            status="built",
            participant_count=len(nodes),
            key_supporters=supporters[:3],
            key_opponents=opponents[:3],
            consensus_signals=consensus_signals[:5],
            divergence_signals=divergence_signals[:5],
            nodes=nodes,
        )

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

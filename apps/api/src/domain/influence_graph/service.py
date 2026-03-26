from __future__ import annotations

from typing import Any

from schemas.influence_graph import InfluenceGraphPayload, InfluenceGraphRound, ParticipantInfluenceEdge


class InfluenceGraphService:
    def build_payload(self, event_id: str, rounds: list[dict[str, Any]]) -> InfluenceGraphPayload:
        leader_history: list[dict[str, str]] = []
        risk_history: list[dict[str, str]] = []
        graph_rounds: list[InfluenceGraphRound] = []

        for round_item in rounds:
            round_id = str(round_item.get("round_id") or "")
            order = int(round_item.get("order") or 0)
            actions = list(round_item.get("participant_actions") or [])
            states = list(round_item.get("participant_states") or [])
            market_state = str((round_item.get("market_state") or {}).get("state") or "DORMANT")
            state_map = {
                str(item.get("participant_id") or ""): item
                for item in states
                if str(item.get("participant_id") or "").strip()
            }
            edges: list[ParticipantInfluenceEdge] = []
            current_leaders: list[dict[str, str]] = []
            current_risks: list[dict[str, str]] = []

            for action in actions:
                participant_id = str(action.get("participant_id") or "")
                if not participant_id:
                    continue
                participant_family = str(action.get("participant_family") or state_map.get(participant_id, {}).get("participant_family") or "unknown")
                action_type = str(action.get("action_type") or "")
                polarity = str(action.get("polarity") or self._polarity_for_action(action, state_map.get(participant_id) or {}))

                if action_type == "first_move":
                    edges.append(
                        ParticipantInfluenceEdge(
                            source_participant_id="event_seed",
                            source_participant_family="event_seed",
                            target_participant_id=participant_id,
                            target_participant_family=participant_family,
                            round_id=round_id,
                            order=order,
                            influence_type="seed_activation",
                            polarity=polarity,
                            strength=0.92,
                            reason="The event seed directly activates the first mover.",
                        )
                    )
                    current_leaders.append(
                        {
                            "participant_id": participant_id,
                            "participant_family": participant_family,
                            "polarity": polarity,
                        }
                    )
                    continue

                if action_type == "follow_on":
                    sources = [item for item in current_leaders if item["participant_id"] != participant_id] or [
                        item for item in leader_history if item["participant_id"] != participant_id
                    ]
                    if not sources:
                        sources = [
                            {
                                "participant_id": "event_seed",
                                "participant_family": "event_seed",
                                "polarity": polarity,
                            }
                        ]
                    for source in sources[:2]:
                        edges.append(
                            ParticipantInfluenceEdge(
                                source_participant_id=str(source["participant_id"]),
                                source_participant_family=str(source["participant_family"]),
                                target_participant_id=participant_id,
                                target_participant_family=participant_family,
                                round_id=round_id,
                                order=order,
                                influence_type=self._influence_type(source_family=str(source["participant_family"]), action_type=action_type),
                                polarity=polarity,
                                strength=self._strength_from_state(state_map.get(participant_id) or {}, base=0.72),
                                reason="Follow-on action confirms the narrative transmission path.",
                            )
                        )
                    current_leaders.append(
                        {
                            "participant_id": participant_id,
                            "participant_family": participant_family,
                            "polarity": polarity,
                        }
                    )
                    continue

                if action_type in {"risk_watch", "exit"}:
                    sources = [item for item in current_risks if item["participant_id"] != participant_id] or [
                        item for item in risk_history if item["participant_id"] != participant_id
                    ] or [
                        item for item in leader_history if item["participant_id"] != participant_id
                    ]
                    if not sources:
                        sources = [
                            {
                                "participant_id": "event_seed",
                                "participant_family": "event_seed",
                                "polarity": "bearish",
                            }
                        ]
                    for source in sources[:1]:
                        edges.append(
                            ParticipantInfluenceEdge(
                                source_participant_id=str(source["participant_id"]),
                                source_participant_family=str(source["participant_family"]),
                                target_participant_id=participant_id,
                                target_participant_family=participant_family,
                                round_id=round_id,
                                order=order,
                                influence_type="risk_signal",
                                polarity="bearish",
                                strength=self._strength_from_state(state_map.get(participant_id) or {}, base=0.68),
                                reason="Risk pressure pushes the participant into watch or exit behavior.",
                            )
                        )
                    current_risks.append(
                        {
                            "participant_id": participant_id,
                            "participant_family": participant_family,
                            "polarity": "bearish",
                        }
                    )

            graph_rounds.append(
                InfluenceGraphRound(
                    event_id=event_id,
                    round_id=round_id,
                    order=order,
                    market_state=market_state,
                    edges=edges,
                )
            )
            leader_history.extend(current_leaders)
            risk_history.extend(current_risks)

        latest_round_id = graph_rounds[-1].round_id if graph_rounds else ""
        return InfluenceGraphPayload(
            event_id=event_id,
            status="ready" if graph_rounds else "missing",
            latest_round_id=latest_round_id,
            rounds=graph_rounds,
        )

    def _polarity_for_action(self, action: dict[str, Any], state: dict[str, Any]) -> str:
        stance = str(state.get("stance") or "").strip().lower()
        action_type = str(action.get("action_type") or "").strip().lower()
        if action_type in {"risk_watch", "exit"}:
            return "bearish"
        if stance in {"bullish", "constructive"}:
            return "bullish"
        if stance in {"skeptical", "bearish", "watch"}:
            return "bearish"
        return "neutral"

    def _influence_type(self, *, source_family: str, action_type: str) -> str:
        if action_type != "follow_on":
            return "signal_confirmation"
        if source_family == "media_sentiment":
            return "narrative_amplification"
        if source_family in {"industry_research", "supply_chain_channel"}:
            return "fundamental_validation"
        return "momentum_confirmation"

    def _strength_from_state(self, state: dict[str, Any], *, base: float) -> float:
        authority = float(state.get("authority_weight") or 0.0)
        confidence = float(state.get("confidence") or 0.0)
        return round(min(0.98, base + authority * 0.18 + confidence * 0.08), 2)

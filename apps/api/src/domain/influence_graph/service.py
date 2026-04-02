from __future__ import annotations

from typing import Any

from schemas.influence_graph import InfluenceGraphPayload, InfluenceGraphRound, ParticipantInfluenceEdge


class InfluenceGraphService:
    def build_payload(self, event_id: str, rounds: list[dict[str, Any]]) -> InfluenceGraphPayload:
        graph_rounds: list[InfluenceGraphRound] = []

        for round_item in rounds:
            round_id = str(round_item.get("round_id") or "")
            order = int(round_item.get("order") or 0)
            market_state = str((round_item.get("market_state") or {}).get("state") or "DORMANT")
            explicit_edges = list(round_item.get("influence_edges") or [])
            if explicit_edges:
                edges = [
                    edge if isinstance(edge, ParticipantInfluenceEdge) else ParticipantInfluenceEdge(**edge)
                    for edge in explicit_edges
                ]
            else:
                edges = self._derive_edges_from_actions(round_id=round_id, order=order, round_item=round_item)
            graph_rounds.append(
                InfluenceGraphRound(
                    event_id=event_id,
                    round_id=round_id,
                    order=order,
                    market_state=market_state,
                    edges=edges,
                )
            )

        latest_round_id = graph_rounds[-1].round_id if graph_rounds else ""
        return InfluenceGraphPayload(
            event_id=event_id,
            status="ready" if graph_rounds else "missing",
            latest_round_id=latest_round_id,
            rounds=graph_rounds,
        )

    def _derive_edges_from_actions(
        self,
        *,
        round_id: str,
        order: int,
        round_item: dict[str, Any],
    ) -> list[ParticipantInfluenceEdge]:
        actions = list(round_item.get("participant_actions") or [])
        states = list(round_item.get("participant_states") or [])
        state_map = {
            str(item.get("participant_id") or ""): item
            for item in states
            if str(item.get("participant_id") or "").strip()
        }
        bullish_sources = [item for item in actions if str(item.get("action_name") or "") in {"INIT_BUY", "ADD_BUY", "BROADCAST_BULL"}]
        bearish_sources = [item for item in actions if str(item.get("action_name") or "") in {"REDUCE", "EXIT", "BROADCAST_BEAR"}]
        edges: list[ParticipantInfluenceEdge] = []

        for target in actions:
            participant_id = str(target.get("participant_id") or "")
            participant_family = str(target.get("participant_family") or state_map.get(participant_id, {}).get("participant_family") or "unknown")
            action_name = str(target.get("action_name") or "")
            if action_name in {"INIT_BUY", "ADD_BUY", "BROADCAST_BULL"}:
                sources = [item for item in bullish_sources if str(item.get("participant_id") or "") != participant_id]
                polarity = "bullish"
                influence_type = "trade_confirmation"
                effect_on = "entry_bias"
            elif action_name in {"REDUCE", "EXIT", "BROADCAST_BEAR"}:
                sources = [item for item in bearish_sources if str(item.get("participant_id") or "") != participant_id]
                polarity = "bearish"
                influence_type = "risk_signal"
                effect_on = "risk_bias"
            else:
                continue
            for source in sources[:2]:
                source_id = str(source.get("participant_id") or "")
                source_family = str(source.get("participant_family") or state_map.get(source_id, {}).get("participant_family") or "unknown")
                edges.append(
                    ParticipantInfluenceEdge(
                        source_participant_id=source_id,
                        source_participant_family=source_family,
                        target_participant_id=participant_id,
                        target_participant_family=participant_family,
                        round_id=round_id,
                        order=order,
                        influence_type=influence_type,
                        polarity=polarity,
                        strength=round(min(0.95, float(source.get("confidence") or 0.0) * 0.8 + 0.2), 2),
                        reason=f"{source_id} influences {participant_id} through {action_name.lower()}.",
                        lag_windows=1,
                        activation_condition=f"after:{str(source.get('action_name') or '').lower()}",
                        expiration_condition=f"until_round:{order + 1}",
                        effect_on=effect_on,
                    )
                )
        return edges

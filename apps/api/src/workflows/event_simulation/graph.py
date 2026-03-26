from __future__ import annotations

from dataclasses import replace

from schemas.simulation import (
    SIMULATION_ACTION_DISPLAY_TYPES,
    SimulationParticipantState,
    SimulationParticipantUpdate,
    SimulationRoundPlan,
    SimulationRoundResult,
)

_ROLE_STATE_PROGRESSION = {
    "first_move": ("engaged", "confirmed", "accelerating", "de_risking", "settled"),
    "follow_on": ("monitoring", "engaged", "confirming", "scaling", "de_risking"),
    "risk_watch": ("monitoring", "monitoring", "challenging", "hedging", "settled"),
}


def build_event_simulation_graph(*, rounds: list[SimulationRoundPlan], dominant_scenario: str) -> dict[str, object]:
    return {
        "name": "event_simulation",
        "dominant_scenario": dominant_scenario,
        "round_count": len(rounds),
        "nodes": [round_plan.round_id for round_plan in rounds],
    }


def execute_event_simulation_graph(
    *,
    rounds: list[SimulationRoundPlan],
    participant_states: list[SimulationParticipantState],
    dominant_scenario: str,
    graph_status: str,
) -> tuple[list[SimulationRoundResult], list[SimulationParticipantState]]:
    current_states = list(participant_states)
    round_results: list[SimulationRoundResult] = []
    for round_plan in rounds:
        next_states: list[SimulationParticipantState] = []
        participant_updates: list[SimulationParticipantUpdate] = []
        round_reason_codes = list(round_plan.reason_codes) + [
            f"dominant_scenario:{dominant_scenario}",
            f"graph_status:{graph_status}",
        ]
        for state in current_states:
            progression = _ROLE_STATE_PROGRESSION.get(state.role, _ROLE_STATE_PROGRESSION["risk_watch"])
            next_state = progression[min(round_plan.order - 1, len(progression) - 1)]
            action_name = _derive_action_name(state.role, round_plan.order, next_state, state.stance)
            action_type = SIMULATION_ACTION_DISPLAY_TYPES[action_name]
            reason_codes = round_reason_codes + [
                f"participant:{state.participant_id}",
                f"action:{action_type}",
                f"action_name:{action_name}",
                f"role:{state.role}",
                f"stance:{state.stance}",
            ]
            participant_updates.append(
                SimulationParticipantUpdate(
                    participant_id=state.participant_id,
                    action_type=action_type,
                    previous_state=state.state,
                    next_state=next_state,
                    round_id=round_plan.round_id,
                    actor_id=state.participant_id,
                    target_id=_derive_target_id(state, action_name),
                    action_name=action_name,
                    confidence=state.confidence,
                    reason_code=reason_codes[0] if reason_codes else "",
                    reason_codes=reason_codes,
                )
            )
            next_states.append(replace(state, state=next_state, reason_codes=reason_codes))
        round_results.append(
            SimulationRoundResult(
                round_id=round_plan.round_id,
                order=round_plan.order,
                focus=round_plan.focus,
                objective=round_plan.objective,
                status="completed",
                participant_updates=participant_updates,
                participant_states=[state.to_dict() for state in next_states],
                reason_codes=round_reason_codes,
            )
        )
        current_states = next_states
    return round_results, current_states


def _derive_action_name(role: str, order: int, next_state: str, stance: str) -> str:
    if next_state in {"de_risking", "hedging", "settled"}:
        return "EXIT"
    if role == "first_move" and order == 1:
        return "LEAD"
    if role == "follow_on":
        return "FOLLOW"
    if role == "risk_watch":
        return "WATCH"
    if stance in {"bullish", "constructive"}:
        return "BROADCAST_BULL"
    if stance in {"skeptical", "bearish"}:
        return "BROADCAST_BEAR"
    return "VALIDATE"


def _derive_target_id(state: SimulationParticipantState, action_name: str) -> str:
    if action_name in {"LEAD", "FOLLOW"}:
        return state.trigger_signals[0] if state.trigger_signals else "market"
    if action_name in {"BROADCAST_BULL", "BROADCAST_BEAR"}:
        return state.participant_family
    if action_name == "EXIT":
        return state.invalidation_signals[0] if state.invalidation_signals else "risk_line"
    return "self"

# Backend Dev Agent touched runtime story scope.

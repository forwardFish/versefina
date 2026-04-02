from __future__ import annotations

from schemas.simulation import SimulationRoundResult, SimulationTimelineEntry, SimulationTimelineSummary


def build_simulation_timeline(round_results: list[SimulationRoundResult]) -> SimulationTimelineSummary:
    if not round_results:
        return SimulationTimelineSummary(status="timeline_incomplete")

    first_move: list[SimulationTimelineEntry] = []
    follow_on: list[SimulationTimelineEntry] = []
    exit_chain: list[SimulationTimelineEntry] = []
    turning_points: list[str] = []
    seen_first_move: set[str] = set()
    seen_follow_on: set[str] = set()
    seen_exit: set[str] = set()

    for round_result in round_results:
        round_turning = False
        for update in round_result.participant_updates:
            action_name = str(update.action_name or "").upper()
            entry = SimulationTimelineEntry(
                participant_id=update.participant_id,
                round_id=round_result.round_id,
                order=round_result.order,
                action_type=update.action_type,
                state_before=update.previous_state,
                state_after=update.next_state,
                execution_window=update.execution_window,
                target_symbol=update.target_symbol,
                order_value=update.order_value,
                reason_codes=list(update.reason_codes),
            )
            if action_name == "INIT_BUY" and update.participant_id not in seen_first_move:
                first_move.append(entry)
                seen_first_move.add(update.participant_id)
            elif action_name in {"ADD_BUY", "BROADCAST_BULL"} and update.participant_id not in seen_follow_on:
                follow_on.append(entry)
                seen_follow_on.add(update.participant_id)
            elif action_name in {"REDUCE", "EXIT", "BROADCAST_BEAR"} and update.participant_id not in seen_exit:
                exit_chain.append(entry)
                seen_exit.add(update.participant_id)
                round_turning = True
        if round_turning or "Risk" in round_result.focus or "Close" in round_result.focus:
            turning_points.append(round_result.round_id)

    status = "complete" if first_move or follow_on or exit_chain else "timeline_incomplete"
    return SimulationTimelineSummary(
        status=status,
        first_move=first_move,
        follow_on=follow_on,
        exit_chain=exit_chain,
        turning_points=turning_points,
    )

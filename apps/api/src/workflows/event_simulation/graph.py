from __future__ import annotations

from dataclasses import replace
from math import floor
from typing import Any

from schemas.influence_graph import ParticipantInfluenceEdge
from schemas.simulation import (
    SIMULATION_ACTION_DISPLAY_TYPES,
    SimulationParticipantState,
    SimulationParticipantUpdate,
    SimulationRoundPlan,
    SimulationRoundResult,
)

_SUPPORTIVE_STANCES = {"bullish", "constructive"}
_DEFENSIVE_STANCES = {"watch", "skeptical", "bearish", "neutral"}
_BULLISH_ACTIONS = {"INIT_BUY", "ADD_BUY", "BROADCAST_BULL"}
_BEARISH_ACTIONS = {"REDUCE", "EXIT", "BROADCAST_BEAR"}

_BULLISH_FAMILY_TARGETS: dict[str, tuple[str, ...]] = {
    "retail_fast_money": ("institution_confirmation", "media_sentiment", "quant_risk_budget", "policy_research"),
    "institution_confirmation": ("quant_risk_budget", "retail_fast_money", "media_sentiment", "policy_research"),
    "industry_research": ("institution_confirmation", "policy_research", "quant_risk_budget", "media_sentiment"),
    "policy_research": ("institution_confirmation", "quant_risk_budget", "retail_fast_money"),
    "quant_risk_budget": ("retail_fast_money", "institution_confirmation"),
    "media_sentiment": ("retail_fast_money", "quant_risk_budget", "institution_confirmation"),
    "supply_chain_channel": ("industry_research", "institution_confirmation", "media_sentiment", "retail_fast_money"),
}

_BEARISH_FAMILY_TARGETS: dict[str, tuple[str, ...]] = {
    "risk_control": (
        "institution_confirmation",
        "retail_fast_money",
        "quant_risk_budget",
        "media_sentiment",
        "supply_chain_channel",
        "industry_research",
        "policy_research",
    ),
    "policy_research": ("institution_confirmation", "quant_risk_budget", "retail_fast_money"),
    "quant_risk_budget": ("institution_confirmation", "retail_fast_money", "media_sentiment"),
    "media_sentiment": ("retail_fast_money", "quant_risk_budget", "institution_confirmation"),
    "institution_confirmation": ("quant_risk_budget", "retail_fast_money"),
}


def build_event_simulation_graph(
    *,
    event_id: str,
    rounds: list[SimulationRoundPlan],
    dominant_scenario: str,
    graph_status: str,
    focus_symbols: list[str],
) -> dict[str, object]:
    return {
        "name": "event_simulation_closed_loop",
        "event_id": event_id,
        "dominant_scenario": dominant_scenario,
        "graph_status": graph_status,
        "round_count": len(rounds),
        "focus_symbols": list(focus_symbols),
        "nodes": [
            {
                "round_id": round_plan.round_id,
                "order": round_plan.order,
                "day_index": round_plan.day_index,
                "trade_date": round_plan.trade_date,
                "execution_window": round_plan.execution_window,
                "focus": round_plan.focus,
            }
            for round_plan in rounds
        ],
    }


def execute_event_simulation_graph(
    *,
    rounds: list[SimulationRoundPlan],
    participant_states: list[SimulationParticipantState],
    dominant_scenario: str,
    graph_status: str,
    focus_symbols: list[str],
    focus_symbol: str,
    watchpoints: list[str],
    invalidation_conditions: list[str],
    confirmation_signals: list[str],
    reference_price: float,
    reference_price_source: str,
    lot_size: int,
) -> tuple[list[SimulationRoundResult], list[SimulationParticipantState]]:
    current_states = list(participant_states)
    round_results: list[SimulationRoundResult] = []
    active_edges: list[dict[str, Any]] = []
    previous_market_metrics: dict[str, Any] = {
        "state": "DORMANT",
        "net_flow": 0.0,
        "buy_clone_count": 0,
        "sell_clone_count": 0,
        "crowding_score": 0.0,
        "fragility_score": 0.0,
        "dominant_support_chain": [],
        "opposition_strength": 0.0,
        "invalidation_hits": 0,
    }
    resolved_focus_symbol = str(focus_symbol or (focus_symbols[0] if focus_symbols else ""))

    for round_plan in rounds:
        incoming_by_target = _active_influence_by_target(active_edges, round_plan.order)
        participant_updates: list[SimulationParticipantUpdate] = []
        next_states: list[SimulationParticipantState] = []
        round_reason_codes = list(round_plan.reason_codes) + [
            f"dominant_scenario:{dominant_scenario}",
            f"graph_status:{graph_status}",
            f"trade_date:{round_plan.trade_date}",
        ]

        for state in current_states:
            incoming_edges = incoming_by_target.get(state.participant_id, [])
            decision = _decide_action(
                state=state,
                round_plan=round_plan,
                dominant_scenario=dominant_scenario,
                market_metrics=previous_market_metrics,
                incoming_edges=incoming_edges,
                focus_symbol=resolved_focus_symbol,
                watchpoints=watchpoints,
                invalidation_conditions=invalidation_conditions,
                confirmation_signals=confirmation_signals,
                reference_price=reference_price,
                reference_price_source=reference_price_source,
                lot_size=lot_size,
            )
            participant_updates.append(
                SimulationParticipantUpdate(
                    participant_id=state.participant_id,
                    action_type=SIMULATION_ACTION_DISPLAY_TYPES[decision["action_name"]],
                    previous_state=state.state,
                    next_state=str(decision["next_state"]),
                    round_id=round_plan.round_id,
                    actor_id=state.participant_id,
                    target_id=str(decision["target_id"]),
                    action_name=str(decision["action_name"]),
                    confidence=float(decision["confidence"]),
                    reason_code=str(decision["reason_codes"][0]) if decision["reason_codes"] else "",
                    reason_codes=list(decision["reason_codes"]),
                    execution_window=round_plan.execution_window,
                    day_index=round_plan.day_index,
                    trade_date=round_plan.trade_date,
                    target_symbol=resolved_focus_symbol,
                    order_side=str(decision["order_side"]),
                    order_value=float(decision["order_value"]),
                    order_value_range_min=float(decision["order_value_range_min"]),
                    order_value_range_max=float(decision["order_value_range_max"]),
                    reference_price=float(decision["reference_price"]),
                    reference_price_source=str(decision["reference_price_source"]),
                    lot_size=int(decision["lot_size"]),
                    trade_quantity=float(decision["trade_quantity"]),
                    trade_unit_label=str(decision["trade_unit_label"]),
                    position_before=float(decision["position_before"]),
                    position_after=float(decision["position_after"]),
                    position_qty_before=float(decision["position_qty_before"]),
                    position_qty_after=float(decision["position_qty_after"]),
                    holding_qty_after=float(decision["holding_qty_after"]),
                    cash_before=float(decision["cash_before"]),
                    cash_after=float(decision["cash_after"]),
                    influenced_by=list(decision["influenced_by"]),
                    evidence_trace=list(decision["evidence_trace"]),
                    effect_summary=str(decision["effect_summary"]),
                )
            )
            next_states.append(
                replace(
                    state,
                    state=str(decision["next_state"]),
                    cash_available=float(decision["cash_after"]),
                    current_positions=dict(decision["current_positions"]),
                    current_position_quantities=dict(decision["current_position_quantities"]),
                    confidence=float(decision["confidence"]),
                    reason_codes=list(decision["reason_codes"]),
                )
            )

        market_metrics = _build_market_metrics(
            round_plan=round_plan,
            participant_updates=participant_updates,
            participant_states=next_states,
            previous_market_metrics=previous_market_metrics,
        )
        belief_metrics = _build_belief_metrics(
            participant_states=next_states,
            participant_updates=participant_updates,
            market_metrics=market_metrics,
        )
        new_edges = _build_influence_edges(
            round_plan=round_plan,
            participant_updates=participant_updates,
            participant_states=next_states,
            market_metrics=market_metrics,
            focus_symbol=resolved_focus_symbol,
        )
        active_edges.extend(edge.to_dict() for edge in new_edges)
        buy_clone_count = sum(1 for update in participant_updates if update.order_side == "buy")
        sell_clone_count = sum(1 for update in participant_updates if update.order_side == "sell")
        new_entry_clone_count = sum(1 for update in participant_updates if update.action_name == "INIT_BUY")
        exit_clone_count = sum(1 for update in participant_updates if update.action_name == "EXIT")
        round_results.append(
            SimulationRoundResult(
                round_id=round_plan.round_id,
                order=round_plan.order,
                focus=round_plan.focus,
                objective=round_plan.objective,
                status="completed",
                execution_window=round_plan.execution_window,
                day_index=round_plan.day_index,
                trade_date=round_plan.trade_date,
                is_trading_day=round_plan.is_trading_day,
                is_incremental_generated=round_plan.is_incremental_generated,
                actions_count=len(participant_updates),
                buy_clone_count=buy_clone_count,
                sell_clone_count=sell_clone_count,
                new_entry_clone_count=new_entry_clone_count,
                exit_clone_count=exit_clone_count,
                participant_updates=participant_updates,
                participant_states=[state.to_dict() for state in next_states],
                influence_edges=[edge.to_dict() for edge in new_edges],
                market_metrics=market_metrics,
                belief_metrics=belief_metrics,
                reason_codes=round_reason_codes,
            )
        )
        current_states = next_states
        previous_market_metrics = market_metrics

    return round_results, current_states


def _active_influence_by_target(active_edges: list[dict[str, Any]], round_order: int) -> dict[str, list[dict[str, Any]]]:
    by_target: dict[str, list[dict[str, Any]]] = {}
    for edge in active_edges:
        start_order = int(edge.get("order") or 0) + int(edge.get("lag_windows") or 1)
        end_order = int(edge.get("expiry_order") or 0)
        if round_order < start_order or (end_order and round_order > end_order):
            continue
        target = str(edge.get("target_participant_id") or "")
        if not target:
            continue
        by_target.setdefault(target, []).append(edge)
    for target in by_target:
        by_target[target].sort(key=lambda item: float(item.get("strength") or 0.0), reverse=True)
    return by_target


def _decide_action(
    *,
    state: SimulationParticipantState,
    round_plan: SimulationRoundPlan,
    dominant_scenario: str,
    market_metrics: dict[str, Any],
    incoming_edges: list[dict[str, Any]],
    focus_symbol: str,
    watchpoints: list[str],
    invalidation_conditions: list[str],
    confirmation_signals: list[str],
    reference_price: float,
    reference_price_source: str,
    lot_size: int,
) -> dict[str, Any]:
    current_positions = dict(state.current_positions)
    current_position_quantities = dict(state.current_position_quantities)
    position_before = float(current_positions.get(focus_symbol, 0.0)) if focus_symbol else 0.0
    position_qty_before = float(current_position_quantities.get(focus_symbol, 0.0)) if focus_symbol else 0.0
    cash_before = float(state.cash_available)
    remaining_capacity = max(0.0, float(state.max_event_exposure) - position_before)
    position_ratio = position_before / max(float(state.max_event_exposure), 1.0)
    bull_influence = round(
        sum(float(edge.get("strength") or 0.0) for edge in incoming_edges if str(edge.get("polarity") or "") == "bullish"),
        2,
    )
    bear_influence = round(
        sum(float(edge.get("strength") or 0.0) for edge in incoming_edges if str(edge.get("polarity") or "") == "bearish"),
        2,
    )
    scenario_bias = _scenario_bias(state.stance, dominant_scenario)
    window_bias = _window_bias(state, round_plan.execution_window)
    day_bias = _day_bias(state, round_plan.day_index)
    crowding_score = float(market_metrics.get("crowding_score") or 0.0)
    fragility_score = float(market_metrics.get("fragility_score") or 0.0)
    previous_state = str(market_metrics.get("state") or "DORMANT")
    supportive_signal = 0.08 if state.stance in _SUPPORTIVE_STANCES else -0.06 if state.stance in _DEFENSIVE_STANCES else 0.0
    validation_score = round(
        min(
            1.0,
            max(
                0.0,
                state.confidence * 0.42
                + state.authority_weight * 0.18
                + state.influence_weight * 0.12
                + bull_influence * 0.3
                + supportive_signal
                + scenario_bias
                + window_bias
                + day_bias,
            ),
        ),
        2,
    )
    risk_score = round(
        min(
            1.0,
            max(
                0.0,
                bear_influence * 0.45
                + fragility_score * 0.28
                + crowding_score * 0.18
                + (0.14 if state.participant_family == "risk_control" else 0.0)
                + (0.08 if previous_state in {"FRAGILE", "INVALIDATED"} else 0.0)
                + (0.08 if round_plan.day_index >= 3 and previous_state in {"PROPAGATING", "CROWDED"} else 0.0),
            ),
        ),
        2,
    )
    entry_score = round(min(1.0, max(0.0, validation_score - risk_score + 0.12 * (1.0 - position_ratio))), 2)
    add_score = round(min(1.0, max(0.0, validation_score + bull_influence * 0.18 - risk_score + position_ratio * 0.06)), 2)
    reduce_score = round(min(1.0, max(0.0, risk_score + crowding_score * 0.25 - validation_score * 0.12)), 2)
    exit_score = round(min(1.0, max(0.0, risk_score + fragility_score * 0.24 + max(0.0, crowding_score - 0.62) * 0.22)), 2)
    latency_locked = round_plan.order <= int(state.reaction_latency) and state.participant_family != "risk_control"
    influenced_by = [dict(edge) for edge in incoming_edges[:3]]
    evidence_trace = [
        {"kind": "metric", "metric": "validation_score", "value": validation_score, "threshold": state.entry_threshold},
        {"kind": "metric", "metric": "add_score", "value": add_score, "threshold": state.add_threshold},
        {"kind": "metric", "metric": "reduce_score", "value": reduce_score, "threshold": state.reduce_threshold},
        {"kind": "metric", "metric": "exit_score", "value": exit_score, "threshold": state.exit_threshold},
        {"kind": "market", "metric": "crowding_score", "value": crowding_score},
        {"kind": "market", "metric": "fragility_score", "value": fragility_score},
        {"kind": "market", "metric": "net_flow", "value": float(market_metrics.get("net_flow") or 0.0)},
        {"kind": "state", "metric": "previous_market_state", "value": previous_state},
    ]
    if confirmation_signals:
        evidence_trace.append({"kind": "signal", "metric": "confirmation_signals", "value": list(confirmation_signals[:2])})
    if invalidation_conditions:
        evidence_trace.append({"kind": "signal", "metric": "invalidation_conditions", "value": list(invalidation_conditions[:2])})
    if watchpoints:
        evidence_trace.append({"kind": "signal", "metric": "watchpoints", "value": list(watchpoints[:2])})

    action_name = "WATCH"
    if position_before > 0:
        if (
            round_plan.day_index >= 4
            and previous_state in {"CROWDED", "FRAGILE", "INVALIDATED"}
            and state.participant_family in {"retail_fast_money", "quant_risk_budget", "institution_confirmation"}
        ):
            action_name = "EXIT" if position_ratio >= 0.48 else "REDUCE"
        elif (
            round_plan.day_index >= 2
            and state.role == "leader"
            and bear_influence >= 0.35
            and previous_state in {"PROPAGATING", "CROWDED", "FRAGILE"}
        ):
            action_name = "REDUCE"
        elif exit_score >= state.exit_threshold or previous_state == "INVALIDATED":
            action_name = "EXIT"
        elif reduce_score >= state.reduce_threshold:
            action_name = "REDUCE"
        elif not latency_locked and add_score >= state.add_threshold and remaining_capacity > 0 and previous_state != "INVALIDATED":
            action_name = "ADD_BUY"
        elif bull_influence >= 0.38 and state.participant_family in {"industry_research", "policy_research", "media_sentiment"}:
            action_name = "BROADCAST_BULL"
        elif (
            risk_score >= 0.52
            and round_plan.day_index >= 3
            and state.participant_family in {"risk_control", "policy_research", "media_sentiment"}
        ):
            action_name = "BROADCAST_BEAR"
        elif validation_score >= 0.54:
            action_name = "VALIDATE"
    else:
        if (
            state.participant_family == "risk_control"
            and (
                risk_score >= state.reduce_threshold
                or (round_plan.day_index >= 3 and previous_state in {"CROWDED", "PROPAGATING", "FRAGILE"})
            )
        ):
            action_name = "BROADCAST_BEAR"
        elif latency_locked and entry_score < state.entry_threshold + 0.08:
            action_name = "WATCH" if risk_score >= 0.52 else "VALIDATE"
        elif (
            not latency_locked
            and (
                entry_score >= state.entry_threshold
                or (round_plan.day_index >= 2 and state.role == "follower" and bull_influence >= 0.28 and entry_score >= state.entry_threshold - 0.04)
            )
            and remaining_capacity > 0
            and previous_state != "INVALIDATED"
        ):
            if state.participant_family in {"industry_research", "policy_research"} and bull_influence < 0.32 and validation_score >= 0.57:
                action_name = "VALIDATE"
            else:
                action_name = "INIT_BUY"
        elif state.participant_family in {"industry_research", "supply_chain_channel"} and validation_score >= 0.58:
            action_name = "BROADCAST_BULL"
        elif state.participant_family in {"policy_research", "media_sentiment"} and risk_score >= 0.6:
            action_name = "BROADCAST_BEAR"
        elif validation_score >= 0.56:
            action_name = "VALIDATE"

    order_value = 0.0
    order_range_min = 0.0
    order_range_max = 0.0
    position_after = position_before
    position_qty_after = position_qty_before
    cash_after = cash_before
    order_side = "none"
    trade_quantity = 0.0

    if action_name in {"INIT_BUY", "ADD_BUY"} and focus_symbol:
        ticket = _buy_ticket_size(
            state=state,
            score=entry_score if action_name == "INIT_BUY" else add_score,
            remaining_capacity=remaining_capacity,
            cash_available=cash_before,
            execution_window=round_plan.execution_window,
            day_index=round_plan.day_index,
            previous_state=previous_state,
        )
        trade_quantity = _trade_quantity_for_value(ticket, reference_price, lot_size)
        minimum_lot_value = round(reference_price * max(lot_size, 1), 2)
        if trade_quantity <= 0 and min(remaining_capacity, cash_before) >= minimum_lot_value > 0:
            trade_quantity = float(lot_size)
        if trade_quantity > 0:
            order_side = "buy"
            order_value = round(trade_quantity * reference_price, 2)
            position_after = round(position_before + order_value, 2)
            position_qty_after = round(position_qty_before + trade_quantity, 2)
            cash_after = round(max(0.0, cash_before - order_value), 2)
            current_positions[focus_symbol] = position_after
            current_position_quantities[focus_symbol] = position_qty_after
            order_range_min = round(max(reference_price * max(lot_size, 1), order_value * 0.88), 2)
            order_range_max = round(min(order_value * 1.15, cash_before, remaining_capacity or order_value), 2)
        else:
            action_name = "WATCH"
    elif action_name == "REDUCE" and focus_symbol and position_before > 0:
        trade_quantity = _reduce_quantity(position_qty_before, lot_size, fraction=0.35)
        if trade_quantity > 0:
            order_side = "sell"
            order_value = round(min(position_before, trade_quantity * reference_price), 2)
            position_after = round(max(0.0, position_before - order_value), 2)
            position_qty_after = round(max(0.0, position_qty_before - trade_quantity), 2)
            cash_after = round(cash_before + order_value, 2)
            current_positions[focus_symbol] = position_after
            current_position_quantities[focus_symbol] = position_qty_after
            order_range_min = round(order_value * 0.8, 2)
            order_range_max = round(order_value, 2)
        else:
            action_name = "WATCH"
    elif action_name == "EXIT" and focus_symbol and position_before > 0:
        trade_quantity = float(position_qty_before)
        if trade_quantity > 0:
            order_side = "sell"
            order_value = round(min(position_before, trade_quantity * reference_price), 2)
            position_after = 0.0
            position_qty_after = 0.0
            cash_after = round(cash_before + order_value, 2)
            current_positions[focus_symbol] = 0.0
            current_position_quantities[focus_symbol] = 0.0
            order_range_min = order_value
            order_range_max = order_value
        else:
            action_name = "WATCH"

    target_id = "self"
    if action_name in {"BROADCAST_BULL", "BROADCAST_BEAR"}:
        target_id = focus_symbol or "market_signal"
    elif action_name in {"INIT_BUY", "ADD_BUY", "REDUCE", "EXIT"}:
        target_id = focus_symbol or "market"

    next_state = {
        "IGNORE": state.state,
        "WATCH": "watching",
        "VALIDATE": "validated",
        "INIT_BUY": "engaged",
        "ADD_BUY": "accelerating",
        "REDUCE": "de_risking",
        "EXIT": "exited",
        "BROADCAST_BULL": "broadcasting",
        "BROADCAST_BEAR": "broadcasting",
    }[action_name]
    confidence = round(
        min(
            0.99,
            max(
                0.18,
                state.confidence
                + (0.04 if action_name in _BULLISH_ACTIONS else -0.03 if action_name in _BEARISH_ACTIONS else 0.0)
                + bull_influence * 0.03
                - bear_influence * 0.03,
            ),
        ),
        2,
    )
    reason_codes = [
        f"round:{round_plan.order}",
        f"day_index:{round_plan.day_index}",
        f"trade_date:{round_plan.trade_date}",
        f"participant:{state.participant_id}",
        f"action_name:{action_name}",
        f"validation_score:{validation_score}",
        f"risk_score:{risk_score}",
    ]
    effect_summary = _effect_summary(
        participant_id=state.participant_id,
        action_name=action_name,
        order_value=order_value,
        trade_quantity=trade_quantity,
        bull_influence=bull_influence,
        bear_influence=bear_influence,
        focus_symbol=focus_symbol,
        day_index=round_plan.day_index,
    )
    return {
        "action_name": action_name,
        "next_state": next_state,
        "target_id": target_id,
        "order_side": order_side,
        "order_value": round(order_value, 2),
        "order_value_range_min": round(order_range_min, 2),
        "order_value_range_max": round(order_range_max, 2),
        "reference_price": round(reference_price, 4),
        "reference_price_source": reference_price_source,
        "lot_size": int(lot_size),
        "trade_quantity": round(trade_quantity, 2),
        "trade_unit_label": "股",
        "position_before": round(position_before, 2),
        "position_after": round(position_after, 2),
        "position_qty_before": round(position_qty_before, 2),
        "position_qty_after": round(position_qty_after, 2),
        "holding_qty_after": round(position_qty_after, 2),
        "cash_before": round(cash_before, 2),
        "cash_after": round(cash_after, 2),
        "current_positions": current_positions,
        "current_position_quantities": current_position_quantities,
        "confidence": confidence,
        "reason_codes": reason_codes,
        "influenced_by": influenced_by,
        "evidence_trace": evidence_trace,
        "effect_summary": effect_summary,
    }


def _scenario_bias(stance: str, dominant_scenario: str) -> float:
    normalized_stance = str(stance or "").strip().lower()
    if dominant_scenario == "bull":
        if normalized_stance in _SUPPORTIVE_STANCES:
            return 0.12
        if normalized_stance in _DEFENSIVE_STANCES:
            return -0.04
    if dominant_scenario == "bear":
        if normalized_stance in _SUPPORTIVE_STANCES:
            return -0.06
        if normalized_stance in _DEFENSIVE_STANCES:
            return 0.06
    return 0.03


def _window_bias(state: SimulationParticipantState, execution_window: str) -> float:
    if execution_window in state.preferred_execution_windows:
        return 0.08
    if execution_window in state.avoid_execution_windows:
        return -0.08
    return 0.0


def _day_bias(state: SimulationParticipantState, day_index: int) -> float:
    if state.role == "leader" and day_index == 1:
        return 0.1
    if state.role == "follower" and day_index in {2, 3}:
        return 0.08
    if state.role == "risk_guard" and day_index >= 3:
        return 0.04
    return 0.0


def _buy_ticket_size(
    *,
    state: SimulationParticipantState,
    score: float,
    remaining_capacity: float,
    cash_available: float,
    execution_window: str,
    day_index: int,
    previous_state: str,
) -> float:
    base_ticket = float(state.capital_base) * (0.025 + score * 0.05)
    if execution_window in state.preferred_execution_windows:
        base_ticket *= 1.12
    if execution_window in state.avoid_execution_windows:
        base_ticket *= 0.82
    if state.role == "leader" and day_index == 1:
        base_ticket *= 1.18
    if state.role == "follower" and day_index in {2, 3}:
        base_ticket *= 1.08
    if previous_state in {"CROWDED", "FRAGILE"}:
        base_ticket *= 0.9
    ticket = min(max(0.0, base_ticket), remaining_capacity, cash_available)
    return round(ticket, 2)


def _trade_quantity_for_value(order_value: float, reference_price: float, lot_size: int) -> float:
    if order_value <= 0 or reference_price <= 0:
        return 0.0
    if lot_size <= 0:
        return float(max(0, floor(order_value / reference_price)))
    lot_count = floor(order_value / reference_price / lot_size)
    return float(max(0, lot_count) * lot_size)


def _reduce_quantity(position_qty_before: float, lot_size: int, *, fraction: float) -> float:
    if position_qty_before <= 0:
        return 0.0
    if lot_size <= 0:
        return float(max(0.0, position_qty_before * fraction))
    target_qty = floor(position_qty_before * fraction / lot_size) * lot_size
    if target_qty <= 0 and position_qty_before >= lot_size:
        target_qty = lot_size
    return float(min(position_qty_before, max(0, target_qty)))


def _build_market_metrics(
    *,
    round_plan: SimulationRoundPlan,
    participant_updates: list[SimulationParticipantUpdate],
    participant_states: list[SimulationParticipantState],
    previous_market_metrics: dict[str, Any],
) -> dict[str, Any]:
    signed_flow = 0.0
    buy_clone_count = 0
    sell_clone_count = 0
    bull_broadcasts = 0
    bear_broadcasts = 0
    positive_contributors: list[tuple[str, float]] = []

    for update in participant_updates:
        if update.action_name in {"INIT_BUY", "ADD_BUY"}:
            signed_flow += float(update.order_value)
            buy_clone_count += 1
            positive_contributors.append((update.participant_id, float(update.order_value)))
        elif update.action_name in {"REDUCE", "EXIT"}:
            signed_flow -= float(update.order_value)
            sell_clone_count += 1
        elif update.action_name == "BROADCAST_BULL":
            bull_broadcasts += 1
            positive_contributors.append((update.participant_id, max(1.0, float(update.confidence) * 100.0)))
        elif update.action_name == "BROADCAST_BEAR":
            bear_broadcasts += 1

    total_participants = max(len(participant_states), 1)
    gross_turnover = max(
        sum(abs(float(update.order_value)) for update in participant_updates if float(update.order_value)),
        1.0,
    )
    largest_trade = max((abs(float(update.order_value)) for update in participant_updates), default=0.0)
    breadth = buy_clone_count / total_participants
    concentration_score = round(min(1.0, largest_trade / gross_turnover), 2)
    crowding_score = round(min(1.0, breadth * 1.35 + concentration_score * 0.4 + bull_broadcasts * 0.05), 2)
    fragility_score = round(
        min(
            1.0,
            sell_clone_count / total_participants * 1.7
            + bear_broadcasts * 0.08
            + max(0.0, crowding_score - 0.58) * 0.45
            + (0.05 if round_plan.day_index >= 4 else 0.0),
        ),
        2,
    )
    opposition_strength = round(min(1.0, sell_clone_count / total_participants + bear_broadcasts * 0.09), 2)
    invalidation_hits = bear_broadcasts + (1 if sell_clone_count >= 2 else 0) + (1 if crowding_score >= 0.72 else 0)
    dominant_support_chain = [participant_id for participant_id, _ in sorted(positive_contributors, key=lambda item: item[1], reverse=True)[:3]]
    previous_state = str(previous_market_metrics.get("state") or "DORMANT")
    state = previous_state
    if buy_clone_count == 0 and sell_clone_count == 0 and bull_broadcasts == 0 and previous_state == "DORMANT":
        state = "DORMANT"
    elif previous_state == "DORMANT" and buy_clone_count >= 1:
        state = "IGNITION"
    elif previous_state in {"IGNITION", "DORMANT"} and buy_clone_count >= 2 and crowding_score < 0.68:
        state = "PROPAGATING"
    elif previous_state in {"PROPAGATING", "IGNITION"} and crowding_score >= 0.68 and signed_flow > 0:
        state = "CROWDED"
    elif fragility_score >= 0.5 or sell_clone_count >= 1:
        state = "FRAGILE"
    if opposition_strength >= 0.42 and sell_clone_count >= 2 and signed_flow <= 0:
        state = "INVALIDATED"
    if previous_state == "CROWDED" and fragility_score >= 0.52:
        state = "FRAGILE"

    summaries = {
        "DORMANT": "The clone roster is still observing and has not committed meaningful capital.",
        "IGNITION": "Early capital is entering and the event seed has started to translate into trades.",
        "PROPAGATING": "Follow-on buying is widening and the signal is propagating across families.",
        "CROWDED": "Buying remains positive but the path is becoming crowded and concentrated.",
        "FRAGILE": "Risk pressure is increasing and the market path is losing stability.",
        "INVALIDATED": "Selling and bearish pressure now dominate the event path.",
    }
    return {
        "state": state,
        "execution_window": round_plan.execution_window,
        "day_index": round_plan.day_index,
        "trade_date": round_plan.trade_date,
        "net_flow": round(signed_flow, 2),
        "buy_clone_count": buy_clone_count,
        "sell_clone_count": sell_clone_count,
        "crowding_score": crowding_score,
        "fragility_score": fragility_score,
        "dominant_support_chain": dominant_support_chain,
        "opposition_strength": opposition_strength,
        "invalidation_hits": invalidation_hits,
        "active_participant_count": sum(1 for item in participant_states if item.state not in {"ready", "watching", "validated"}),
        "summary": summaries[state],
    }


def _build_belief_metrics(
    *,
    participant_states: list[SimulationParticipantState],
    participant_updates: list[SimulationParticipantUpdate],
    market_metrics: dict[str, Any],
) -> dict[str, Any]:
    supportive_states = [
        state
        for state in participant_states
        if state.stance in _SUPPORTIVE_STANCES or any(float(value) > 0 for value in state.current_positions.values())
    ]
    opposing_states = [
        state
        for state in participant_states
        if state.stance in _DEFENSIVE_STANCES and not any(float(value) > 0 for value in state.current_positions.values())
    ]
    supportive_value = sum(
        sum(float(value) for value in state.current_positions.values()) + state.authority_weight * state.confidence * 1_000_000
        for state in supportive_states
    )
    opposing_value = sum(state.authority_weight * max(0.05, state.confidence) * 900_000 for state in opposing_states)
    total = max(supportive_value + opposing_value, 1.0)
    consensus_strength = round(min(0.99, supportive_value / total), 2)
    opposition_strength = round(min(0.99, opposing_value / total), 2)
    divergence_index = round(min(0.99, min(consensus_strength, opposition_strength) + market_metrics["fragility_score"] * 0.25), 2)
    supportive_chain = [
        update.participant_id
        for update in participant_updates
        if update.action_name in _BULLISH_ACTIONS
    ][:3]
    opposing_chain = [
        update.participant_id
        for update in participant_updates
        if update.action_name in _BEARISH_ACTIONS
    ][:3]
    return {
        "consensus_strength": consensus_strength,
        "opposition_strength": opposition_strength,
        "divergence_index": divergence_index,
        "key_supporters": supportive_chain or market_metrics.get("dominant_support_chain") or [],
        "key_opponents": opposing_chain,
        "summary": (
            "Bullish conviction still dominates the chain."
            if consensus_strength >= opposition_strength
            else "Opposition strength is compressing the prior consensus."
        ),
    }


def _build_influence_edges(
    *,
    round_plan: SimulationRoundPlan,
    participant_updates: list[SimulationParticipantUpdate],
    participant_states: list[SimulationParticipantState],
    market_metrics: dict[str, Any],
    focus_symbol: str,
) -> list[ParticipantInfluenceEdge]:
    state_lookup = {item.participant_id: item for item in participant_states}
    edges: list[ParticipantInfluenceEdge] = []

    for update in participant_updates:
        source_state = state_lookup.get(update.participant_id)
        if source_state is None:
            continue
        bullish = update.action_name in _BULLISH_ACTIONS
        bearish = update.action_name in _BEARISH_ACTIONS
        if not bullish and not bearish:
            continue
        targets = _select_influence_targets(
            participant_states=participant_states,
            source_state=source_state,
            bullish=bullish,
            bearish=bearish,
        )
        for target_state in targets[:3]:
            strength = _edge_strength(
                source_state=source_state,
                update=update,
                market_metrics=market_metrics,
                bearish=bearish,
            )
            expiry_order = round_plan.order + (2 if bullish else 1)
            edges.append(
                ParticipantInfluenceEdge(
                    source_participant_id=source_state.participant_id,
                    source_participant_family=source_state.participant_family,
                    target_participant_id=target_state.participant_id,
                    target_participant_family=target_state.participant_family,
                    round_id=round_plan.round_id,
                    order=round_plan.order,
                    influence_type=_influence_type(update.action_name, source_state.participant_family),
                    polarity="bearish" if bearish else "bullish",
                    strength=strength,
                    reason=_edge_reason(
                        source_id=source_state.participant_id,
                        action_name=update.action_name,
                        target_id=target_state.participant_id,
                        focus_symbol=focus_symbol,
                        trade_quantity=update.trade_quantity,
                    ),
                    lag_windows=1,
                    activation_condition=f"after:{update.action_name.lower()}",
                    expiration_condition=f"until_round:{expiry_order}",
                    effect_on="risk_bias" if bearish else ("add_bias" if update.action_name == "ADD_BUY" else "entry_bias"),
                )
            )
    return edges


def _select_influence_targets(
    *,
    participant_states: list[SimulationParticipantState],
    source_state: SimulationParticipantState,
    bullish: bool,
    bearish: bool,
) -> list[SimulationParticipantState]:
    preferred_families = ()
    if bullish:
        preferred_families = _BULLISH_FAMILY_TARGETS.get(source_state.participant_family, ())
    elif bearish:
        preferred_families = _BEARISH_FAMILY_TARGETS.get(source_state.participant_family, ())
    candidates = [
        state
        for state in participant_states
        if state.participant_id != source_state.participant_id and state.state != "exited"
    ]
    if preferred_families:
        ordered = [
            state
            for family in preferred_families
            for state in candidates
            if state.participant_family == family
        ]
        if ordered:
            return ordered
    return sorted(candidates, key=lambda item: (-item.authority_weight, -item.influence_weight, item.participant_id))


def _edge_strength(
    *,
    source_state: SimulationParticipantState,
    update: SimulationParticipantUpdate,
    market_metrics: dict[str, Any],
    bearish: bool,
) -> float:
    base = 0.24 + source_state.influence_weight * 0.48 + source_state.authority_weight * 0.12
    if update.order_value:
        base += min(0.12, float(update.order_value) / max(source_state.capital_base, 1.0))
    if bearish:
        base += market_metrics.get("fragility_score", 0.0) * 0.12
    else:
        base += market_metrics.get("crowding_score", 0.0) * 0.05
    return round(min(0.96, base), 2)


def _influence_type(action_name: str, participant_family: str) -> str:
    if action_name in {"REDUCE", "EXIT", "BROADCAST_BEAR"}:
        return "risk_signal"
    if participant_family == "media_sentiment":
        return "narrative_amplification"
    if participant_family in {"industry_research", "supply_chain_channel"}:
        return "fundamental_validation"
    if participant_family == "institution_confirmation":
        return "capital_confirmation"
    return "trade_confirmation"


def _edge_reason(source_id: str, action_name: str, target_id: str, focus_symbol: str, trade_quantity: float) -> str:
    if action_name in {"INIT_BUY", "ADD_BUY"}:
        return (
            f"{source_id} trade on {focus_symbol or 'market'} with {int(trade_quantity or 0)} shares "
            f"lifts follow-through pressure for {target_id}."
        )
    if action_name == "BROADCAST_BULL":
        return f"{source_id} broadcasts bullish confirmation to {target_id}."
    if action_name == "BROADCAST_BEAR":
        return f"{source_id} broadcasts bearish pressure to {target_id}."
    return f"{source_id} de-risking flow warns {target_id}."


def _effect_summary(
    *,
    participant_id: str,
    action_name: str,
    order_value: float,
    trade_quantity: float,
    bull_influence: float,
    bear_influence: float,
    focus_symbol: str,
    day_index: int,
) -> str:
    if action_name in {"INIT_BUY", "ADD_BUY"}:
        return (
            f"Day {day_index}: {participant_id} buys {int(trade_quantity or 0)} shares on {focus_symbol or 'the event symbol'} "
            f"for {round(order_value, 2)} after bullish influence {bull_influence} exceeded bearish influence {bear_influence}."
        )
    if action_name in {"REDUCE", "EXIT"}:
        return (
            f"Day {day_index}: {participant_id} sells {int(trade_quantity or 0)} shares for {round(order_value, 2)} "
            f"because bearish influence {bear_influence} overpowered bullish influence {bull_influence}."
        )
    if action_name == "BROADCAST_BULL":
        return f"Day {day_index}: {participant_id} does not trade but strengthens bullish follow-through for downstream clones."
    if action_name == "BROADCAST_BEAR":
        return f"Day {day_index}: {participant_id} does not trade but injects bearish pressure into downstream clones."
    if action_name == "VALIDATE":
        return f"Day {day_index}: {participant_id} validates the setup and waits for stronger capital or influence confirmation."
    return f"Day {day_index}: {participant_id} stays in observation mode."

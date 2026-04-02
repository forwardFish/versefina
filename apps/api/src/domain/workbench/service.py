from __future__ import annotations

from collections import defaultdict
from typing import Any

from domain.event_casebook.service import EventCasebookService
from domain.event_ingestion.service import EventIngestionService
from domain.event_sandbox.service import EventSandboxService
from domain.finahunt_ingestion.service import FinahuntEventIngestionService
from schemas.command import WorkbenchAskRequest
from schemas.workbench import (
    DecisionTracePayload,
    GraphStageHighlights,
    GraphStagePayload,
    MarketStateTransitionPayload,
    TradeCard,
    TradePulsePayload,
    WorkbenchAskResponse,
    WorkbenchEdge,
    WorkbenchNode,
    WorkbenchReportPayload,
)


_FAMILY_LABELS = {
    "institution_confirmation": "机构",
    "retail_fast_money": "散户",
    "risk_control": "风控",
    "quant_risk_budget": "风控",
    "industry_research": "研究",
    "policy_research": "研究",
    "media_sentiment": "媒体",
    "supply_chain_channel": "渠道",
}

_BUY_ACTIONS = {"INIT_BUY", "ADD_BUY"}
_SELL_ACTIONS = {"REDUCE", "EXIT"}


class WorkbenchService:
    def __init__(
        self,
        *,
        event_casebook: EventCasebookService,
        event_ingestion: EventIngestionService,
        finahunt_ingestion: FinahuntEventIngestionService,
        event_sandbox: EventSandboxService,
    ) -> None:
        self.event_casebook = event_casebook
        self.event_ingestion = event_ingestion
        self.finahunt_ingestion = finahunt_ingestion
        self.event_sandbox = event_sandbox

    def list_clones(self, event_id: str) -> dict[str, Any]:
        event_payload = self._load_event_payload(event_id)
        if event_payload is None:
            return {"event_id": event_id, "status": "not_found", "clones": []}

        participants_payload = self.event_sandbox.load_participants(event_id)
        participants = self._as_list(participants_payload.get("participants"))
        if not participants:
            return {
                "event_id": event_id,
                "status": str(participants_payload.get("status") or "not_found"),
                "clones": [],
            }

        latest_round = self._latest_round(event_id)
        state_lookup = {
            str(item.get("participant_id") or ""): item
            for item in self._as_list((latest_round or {}).get("participant_states"))
        }
        action_lookup = {
            str(item.get("participant_id") or ""): item
            for item in self._as_list((latest_round or {}).get("participant_actions"))
        }
        clones = [
            self._clone_payload(
                participant,
                state_lookup.get(str(participant.get("participant_id") or "")),
                action_lookup.get(str(participant.get("participant_id") or "")),
            )
            for participant in participants
        ]
        return {
            "event_id": event_id,
            "status": str(participants_payload.get("status") or "prepared"),
            "clones": clones,
        }

    def load_clone_detail(self, event_id: str, clone_id: str) -> dict[str, Any]:
        clones_payload = self.list_clones(event_id)
        clones = self._as_list(clones_payload.get("clones"))
        clone = next((item for item in clones if str(item.get("clone_id") or "") == clone_id), None)
        if clone is None:
            return {"event_id": event_id, "status": "not_found", "clone_id": clone_id}
        return {
            "event_id": event_id,
            "status": "ready",
            "clone_id": clone_id,
            "clone": clone,
            "decision_trace": self.load_decision_trace(event_id, clone_id),
        }

    def load_graph_stage(self, event_id: str) -> dict[str, Any]:
        event_payload = self._load_event_payload(event_id)
        if event_payload is None:
            return GraphStagePayload(event_id=event_id, status="not_found").to_dict()

        participants_payload = self.event_sandbox.load_participants(event_id)
        participants = self._as_list(participants_payload.get("participants"))
        replay = self.event_sandbox.load_replay(event_id)
        rounds = self._as_list(replay.get("rounds"))
        latest_round = rounds[-1] if rounds else {}

        nodes: list[WorkbenchNode] = [
            WorkbenchNode(
                node_id="event:market",
                node_type="event",
                label=str(event_payload["record"].get("title") or event_id),
                group="event",
                highlighted=True,
                metadata={
                    "event_type": event_payload["structure"].get("event_type"),
                    "source": event_payload["record"].get("source"),
                    "status": event_payload["status"],
                },
            )
        ]
        edges: list[WorkbenchEdge] = []

        for index, signal in enumerate(self._items(event_payload["structure"].get("monitor_signals")), start=1):
            text = str(signal).strip()
            if not text:
                continue
            node_id = f"signal:{index}"
            nodes.append(
                WorkbenchNode(
                    node_id=node_id,
                    node_type="signal",
                    label=text,
                    group="signal",
                    metadata={"kind": "monitor_signal"},
                )
            )
            edges.append(
                WorkbenchEdge(
                    edge_id=f"event:signal:{index}",
                    edge_type="event",
                    source="event:market",
                    target=node_id,
                    label="事件信号",
                    metadata={"layer": "background"},
                )
            )

        for index, risk in enumerate(self._items(event_payload["structure"].get("invalidation_conditions")), start=1):
            text = str(risk).strip()
            if not text:
                continue
            node_id = f"risk:{index}"
            nodes.append(
                WorkbenchNode(
                    node_id=node_id,
                    node_type="risk",
                    label=text,
                    group="risk",
                    metadata={"kind": "invalidation_condition"},
                )
            )
            edges.append(
                WorkbenchEdge(
                    edge_id=f"event:risk:{index}",
                    edge_type="event",
                    source="event:market",
                    target=node_id,
                    label="失效条件",
                    metadata={"layer": "background"},
                )
            )

        for index, symbol in enumerate(self._symbols_for_event(event_payload), start=1):
            node_id = f"symbol:{symbol}"
            nodes.append(
                WorkbenchNode(
                    node_id=node_id,
                    node_type="symbol",
                    label=symbol,
                    group="market_object",
                    metadata={"kind": "symbol"},
                )
            )
            edges.append(
                WorkbenchEdge(
                    edge_id=f"event:symbol:{index}",
                    edge_type="event",
                    source="event:market",
                    target=node_id,
                    label="映射标的",
                    metadata={"layer": "background"},
                )
            )

        for index, participant in enumerate(participants, start=1):
            participant_id = str(participant.get("participant_id") or "")
            family = str(participant.get("participant_family") or "unknown")
            alias = self._clone_alias(participant_id, index)
            nodes.append(
                WorkbenchNode(
                    node_id=f"clone:{participant_id}",
                    node_type="clone",
                    label=alias,
                    group=family,
                    metadata={
                        "alias": alias,
                        "participant_id": participant_id,
                        "participant_family": family,
                        "family_label": self._family_label(family),
                        "stance": participant.get("stance"),
                        "confidence": participant.get("confidence"),
                        "authority_weight": participant.get("authority_weight"),
                        "capital_bucket": participant.get("capital_bucket"),
                    },
                )
            )

        latest_market = self._as_dict(latest_round.get("market_state"))
        latest_scenario = self._as_dict(latest_round.get("scenario_snapshot"))
        return GraphStagePayload(
            event_id=event_id,
            status="ready",
            shell={
                "title": event_payload["record"].get("title") or event_id,
                "source": event_payload["record"].get("source"),
                "market_state": latest_market.get("state") or "",
                "dominant_scenario": latest_scenario.get("dominant_scenario") or replay.get("dominant_scenario") or "",
                "round_id": latest_round.get("round_id") or "",
                "day_index": latest_round.get("day_index") or 0,
                "trade_date": latest_round.get("trade_date") or "",
                "is_incremental_generated": bool(latest_round.get("is_incremental_generated", False)),
                "actions_count": latest_round.get("actions_count") or 0,
                "buy_clone_count": latest_round.get("buy_clone_count") or 0,
                "sell_clone_count": latest_round.get("sell_clone_count") or 0,
                "new_entry_clone_count": latest_round.get("new_entry_clone_count") or 0,
                "exit_clone_count": latest_round.get("exit_clone_count") or 0,
            },
            event_graph={
                "record": event_payload["record"],
                "structure": event_payload["structure"],
                "mapping": event_payload["mapping"],
                "lineage": event_payload["lineage"],
                "casebook_status": event_payload["status"],
            },
            nodes=nodes,
            edges=edges,
            current_highlights=self._graph_highlights(latest_round),
        ).to_dict()

    def load_trade_pulse(self, event_id: str, round_key: str | None = None, window: str | None = None) -> dict[str, Any]:
        replay = self.event_sandbox.load_replay(event_id)
        if replay.get("status") != "ready":
            return TradePulsePayload(
                event_id=event_id,
                status=str(replay.get("status") or "simulation_missing"),
            ).to_dict()

        rounds = self._as_list(replay.get("rounds"))
        round_payload = self._resolve_round(rounds, round_key)
        if round_payload is None:
            return TradePulsePayload(event_id=event_id, status="not_found").to_dict()

        resolved_window = str(window or round_payload.get("execution_window") or "")
        cards = [
            self._trade_card(round_payload, action, index)
            for index, action in enumerate(self._as_list(round_payload.get("participant_actions")))
            if not resolved_window or str(action.get("execution_window") or round_payload.get("execution_window") or "") == resolved_window
        ]
        market_state = self._as_dict(round_payload.get("market_state"))
        scenario_snapshot = self._as_dict(round_payload.get("scenario_snapshot"))
        return TradePulsePayload(
            event_id=event_id,
            status="ready",
            round_id=str(round_payload.get("round_id") or ""),
            window=resolved_window,
            day_index=int(round_payload.get("day_index") or 0),
            trade_date=str(round_payload.get("trade_date") or ""),
            is_incremental_generated=bool(round_payload.get("is_incremental_generated", False)),
            market_state=str(market_state.get("state") or ""),
            dominant_scenario=str(scenario_snapshot.get("dominant_scenario") or replay.get("dominant_scenario") or ""),
            actions_count=int(round_payload.get("actions_count") or len(cards)),
            buy_clone_count=int(round_payload.get("buy_clone_count") or 0),
            sell_clone_count=int(round_payload.get("sell_clone_count") or 0),
            new_entry_clone_count=int(round_payload.get("new_entry_clone_count") or 0),
            exit_clone_count=int(round_payload.get("exit_clone_count") or 0),
            highlighted_clone_ids=self._unique_strings(action.get("participant_id") for action in self._as_list(round_payload.get("participant_actions"))),
            highlighted_symbols=self._unique_strings(action.get("target_symbol") for action in self._as_list(round_payload.get("participant_actions"))),
            trade_cards=cards,
            market_pulse_summary=self._trade_pulse_summary(round_payload, cards),
        ).to_dict()

    def load_decision_trace(self, event_id: str, clone_id: str, round_key: str | None = None) -> dict[str, Any]:
        replay = self.event_sandbox.load_replay(event_id)
        if replay.get("status") != "ready":
            return DecisionTracePayload(event_id=event_id, status="not_found", clone_id=clone_id).to_dict()

        rounds = self._as_list(replay.get("rounds"))
        round_payload = self._resolve_round(rounds, round_key)
        if round_payload is None:
            return DecisionTracePayload(event_id=event_id, status="not_found", clone_id=clone_id).to_dict()

        states = self._as_list(round_payload.get("participant_states"))
        actions = self._as_list(round_payload.get("participant_actions"))
        state = next((item for item in states if str(item.get("participant_id") or "") == clone_id), {})
        action = next((item for item in actions if str(item.get("participant_id") or "") == clone_id), {})
        clones = self._as_list(self.list_clones(event_id).get("clones"))
        clone_profile = next((item for item in clones if str(item.get("clone_id") or "") == clone_id), {})
        if not clone_profile and not state and not action:
            return DecisionTracePayload(event_id=event_id, status="not_found", clone_id=clone_id).to_dict()

        influence_edges = self._as_list(round_payload.get("influence_edges"))
        incoming = [edge for edge in influence_edges if str(edge.get("target_participant_id") or "") == clone_id]
        outgoing = [edge for edge in influence_edges if str(edge.get("source_participant_id") or "") == clone_id]
        threshold_summary = self._threshold_summary(clone_profile, state)
        seen_signals = self._seen_signals(clone_profile, state, action, incoming)
        decision_chain = [
            {"step": "signals", "label": "当天观察信号", "detail": " / ".join(seen_signals[:4]) or "暂无新增信号"},
            {"step": "thresholds", "label": "决策阈值", "detail": " / ".join(str(item.get("metric") or "") for item in threshold_summary[:4]) or "阈值未返回"},
            {"step": "action", "label": "执行动作", "detail": self._action_label(str(action.get("action_name") or action.get("action_type") or "WATCH"))},
        ]
        return DecisionTracePayload(
            event_id=event_id,
            status="ready",
            clone_id=clone_id,
            round_id=str(round_payload.get("round_id") or ""),
            day_index=int(round_payload.get("day_index") or 0),
            trade_date=str(round_payload.get("trade_date") or ""),
            is_incremental_generated=bool(round_payload.get("is_incremental_generated", False)),
            clone_profile=clone_profile,
            current_state=state or clone_profile,
            seen_signals=seen_signals,
            influenced_by=incoming or self._as_list(action.get("influenced_by")),
            influences=outgoing,
            decision_chain=decision_chain,
            executed_action=action,
            expected_impact=str(action.get("effect_summary") or clone_profile.get("expected_impact") or ""),
            threshold_summary=threshold_summary,
        ).to_dict()

    def load_market_state_transition(self, event_id: str, transition_id: str) -> dict[str, Any]:
        replay = self.event_sandbox.load_replay(event_id)
        if replay.get("status") != "ready":
            return MarketStateTransitionPayload(
                event_id=event_id,
                status=str(replay.get("status") or "simulation_missing"),
                transition_id=transition_id,
            ).to_dict()

        rounds = self._as_list(replay.get("rounds"))
        current_round = self._resolve_round(rounds, transition_id)
        if current_round is None:
            return MarketStateTransitionPayload(event_id=event_id, status="not_found", transition_id=transition_id).to_dict()

        current_index = rounds.index(current_round)
        previous_round = rounds[current_index - 1] if current_index > 0 else {}
        current_market = self._as_dict(current_round.get("market_state"))
        previous_market = self._as_dict(previous_round.get("market_state"))
        triggering_signals: list[str] = []
        for action in self._as_list(current_round.get("participant_actions")):
            triggering_signals.extend(str(code) for code in self._as_list(action.get("reason_codes")))
        for code in self._as_list(current_round.get("reason_codes")):
            triggering_signals.append(str(code))

        return MarketStateTransitionPayload(
            event_id=event_id,
            status="ready",
            transition_id=transition_id,
            from_state=str(previous_market.get("state") or "DORMANT"),
            to_state=str(current_market.get("state") or ""),
            previous_round_id=str(previous_round.get("round_id") or ""),
            current_round_id=str(current_round.get("round_id") or ""),
            day_index=int(current_round.get("day_index") or 0),
            trade_date=str(current_round.get("trade_date") or ""),
            triggering_clones=self._unique_strings(action.get("participant_id") for action in self._as_list(current_round.get("participant_actions"))),
            triggering_edges=self._as_list(current_round.get("influence_edges")),
            triggering_signals=self._unique_strings(triggering_signals),
            market_metrics=current_market,
            summary=str(current_market.get("summary") or self._transition_summary(previous_market, current_market)),
        ).to_dict()

    def load_workbench_report(self, event_id: str) -> dict[str, Any]:
        event_payload = self._load_event_payload(event_id)
        if event_payload is None:
            return WorkbenchReportPayload(event_id=event_id, status="not_found").to_dict()

        replay = self.event_sandbox.load_replay(event_id)
        report = self.event_sandbox.load_report(event_id)
        validation = self.event_sandbox.load_validation(event_id)
        rounds = self._as_list(replay.get("rounds"))
        latest_round = rounds[-1] if rounds else {}
        latest_market = self._as_dict(latest_round.get("market_state"))
        return WorkbenchReportPayload(
            event_id=event_id,
            status="ready" if replay.get("status") == "ready" else str(replay.get("status") or "degraded"),
            replay_summary={
                "run_id": replay.get("run_id"),
                "dominant_scenario": replay.get("dominant_scenario"),
                "generated_day_count": replay.get("generated_day_count"),
                "default_day_count": replay.get("default_day_count"),
                "can_continue": replay.get("can_continue"),
                "latest_round_id": latest_round.get("round_id") or "",
                "latest_trade_date": latest_round.get("trade_date") or "",
                "latest_market_state": latest_market.get("state") or "",
            },
            report=report,
            validation=validation,
            scoreboards={
                "families": self._family_scoreboard(event_id, rounds),
                "clones": self._clone_scoreboard(event_id, rounds),
                "regimes": self._regime_scoreboard(rounds),
            },
            failure_taxonomy=self._failure_taxonomy(rounds, validation),
            provenance={
                "event_source": event_payload["record"].get("source"),
                "lineage": event_payload["lineage"],
                "replay_status": replay.get("status"),
                "report_status": report.get("status"),
                "validation_status": validation.get("status"),
            },
        ).to_dict()

    def ask_workbench(self, event_id: str, payload: WorkbenchAskRequest) -> dict[str, Any]:
        ask_type = str(payload.ask_type or "graph")
        graph_stage = self.load_graph_stage(event_id)
        report = self.load_workbench_report(event_id)
        if graph_stage.get("status") != "ready":
            return WorkbenchAskResponse(
                event_id=event_id,
                status=str(graph_stage.get("status") or "not_found"),
                ask_type=ask_type,
                answer="当前没有可解释的工作台数据。",
                evidence_refs=[],
            ).to_dict()

        highlights = self._as_dict(graph_stage.get("current_highlights"))
        if ask_type == "counterfactual":
            dominant_families = self._items(highlights.get("dominant_family_ids"))
            answer = (
                f"如果关键影响边减弱，{self._family_label(str(dominant_families[0] if dominant_families else 'institution_confirmation'))}"
                " 的带动会先降温，市场状态更容易向脆弱或失效方向偏移。"
            )
        elif payload.clone_id:
            trace = self.load_decision_trace(event_id, payload.clone_id, payload.round_id)
            action = self._as_dict(trace.get("executed_action"))
            answer = (
                f"{self._clone_alias(payload.clone_id)} 当天执行 "
                f"{self._action_label(str(action.get('action_name') or action.get('action_type') or 'WATCH'))}，"
                f"主要因为 {' / '.join(self._as_list(trace.get('seen_signals'))[:3]) or '信号仍在观察中'}。"
            )
        else:
            answer = (
                f"当前主图聚焦第 {int(highlights.get('active_day_index') or 0)} 天，"
                f"活跃 Agent {len(self._as_list(highlights.get('active_clone_ids')))} 个，"
                f"主导情景为 {self._string(self._as_dict(graph_stage.get('shell')).get('dominant_scenario'), 'base')}。"
            )

        return WorkbenchAskResponse(
            event_id=event_id,
            status="ready",
            ask_type=ask_type,
            answer=answer,
            evidence_refs=[
                {"type": "graph-stage", "round_id": highlights.get("active_round_id"), "day_index": highlights.get("active_day_index")},
                {"type": "workbench-report", "status": report.get("status")},
            ],
        ).to_dict()

    def _load_event_payload(self, event_id: str) -> dict[str, Any] | None:
        casebook = self.event_casebook.load_casebook(event_id)
        if casebook is not None:
            record = dict(casebook.record)
            structure = dict(casebook.structure)
            mapping = dict(casebook.mapping)
            status = str(casebook.status or "ready")
        else:
            record_payload = self.event_ingestion.load_record(event_id)
            if record_payload is None:
                return None
            record = record_payload.to_dict()
            structure = dict(record.get("structure") or {})
            mapping = dict(record.get("mapping") or {})
            status = str(record.get("status") or "ingested")
        lineage = self.finahunt_ingestion.load_lineage(event_id)
        return {
            "record": record,
            "structure": structure,
            "mapping": mapping,
            "lineage": lineage.to_dict() if lineage is not None else {},
            "status": status,
        }

    def _latest_round(self, event_id: str) -> dict[str, Any] | None:
        replay = self.event_sandbox.load_replay(event_id)
        rounds = self._as_list(replay.get("rounds"))
        return rounds[-1] if rounds else None

    def _resolve_round(self, rounds: list[dict[str, Any]], round_key: str | None) -> dict[str, Any] | None:
        if not rounds:
            return None
        if not round_key:
            return rounds[-1]
        resolved_key = str(round_key).strip().lower()
        for round_payload in rounds:
            round_id = str(round_payload.get("round_id") or "").strip().lower()
            order = int(round_payload.get("order") or 0)
            if round_id == resolved_key:
                return round_payload
            if resolved_key.isdigit() and order == int(resolved_key):
                return round_payload
        return None

    def _clone_payload(self, participant: dict[str, Any], state: dict[str, Any] | None, action: dict[str, Any] | None) -> dict[str, Any]:
        participant_id = str(participant.get("participant_id") or "")
        resolved_state = state or {}
        resolved_action = action or {}
        return {
            "clone_id": participant_id,
            "participant_id": participant_id,
            "alias": self._clone_alias(participant_id),
            "participant_family": participant.get("participant_family"),
            "family_label": self._family_label(str(participant.get("participant_family") or "")),
            "style_variant": participant.get("style_variant"),
            "stance": participant.get("stance"),
            "confidence": resolved_state.get("confidence", participant.get("confidence")),
            "authority_weight": resolved_state.get("authority_weight", participant.get("authority_weight")),
            "influence_weight": resolved_state.get("influence_weight", participant.get("influence_weight")),
            "state": resolved_state.get("state", participant.get("initial_state")),
            "capital_bucket": participant.get("capital_bucket"),
            "capital_base": participant.get("capital_base"),
            "cash_available": resolved_state.get("cash_available", participant.get("cash_available")),
            "current_positions": resolved_state.get("current_positions", participant.get("current_positions")),
            "max_event_exposure": participant.get("max_event_exposure"),
            "preferred_execution_windows": participant.get("preferred_execution_windows"),
            "avoid_execution_windows": participant.get("avoid_execution_windows"),
            "capital_range": self._capital_range(participant.get("capital_base")),
            "latest_action": resolved_action.get("action_name") or resolved_action.get("action_type") or "",
            "expected_impact": resolved_action.get("effect_summary") or participant.get("expected_impact") or "",
            "entry_threshold": participant.get("entry_threshold"),
            "add_threshold": participant.get("add_threshold"),
            "reduce_threshold": participant.get("reduce_threshold"),
            "exit_threshold": participant.get("exit_threshold"),
        }

    def _trade_card(self, round_payload: dict[str, Any], action: dict[str, Any], index: int) -> TradeCard:
        action_name = str(action.get("action_name") or action.get("action_type") or "")
        target_symbol = str(action.get("target_symbol") or "").strip()
        return TradeCard(
            card_id=f"trade-card:{round_payload.get('round_id')}:{action.get('participant_id')}:{index}",
            participant_id=str(action.get("participant_id") or ""),
            participant_family=str(action.get("participant_family") or "unknown"),
            action_type=action_name or str(action.get("action_type") or ""),
            next_state=str(action.get("next_state") or ""),
            polarity=str(action.get("polarity") or "neutral"),
            symbols=[target_symbol] if target_symbol else [],
            window=str(action.get("execution_window") or round_payload.get("execution_window") or ""),
            day_index=int(action.get("day_index") or round_payload.get("day_index") or 0),
            trade_date=str(action.get("trade_date") or round_payload.get("trade_date") or ""),
            expected_impact=str(action.get("effect_summary") or ""),
            order_side=str(action.get("order_side") or ""),
            order_value=float(action.get("order_value") or 0.0),
            order_value_range_min=float(action.get("order_value_range_min") or 0.0),
            order_value_range_max=float(action.get("order_value_range_max") or 0.0),
            reference_price=float(action.get("reference_price") or 0.0),
            reference_price_source=str(action.get("reference_price_source") or ""),
            lot_size=int(action.get("lot_size") or 0),
            trade_quantity=float(action.get("trade_quantity") or 0.0),
            trade_unit_label=str(action.get("trade_unit_label") or "股"),
            position_before=float(action.get("position_before") or 0.0),
            position_after=float(action.get("position_after") or 0.0),
            position_qty_before=float(action.get("position_qty_before") or 0.0),
            position_qty_after=float(action.get("position_qty_after") or 0.0),
            holding_qty_after=float(action.get("holding_qty_after") or 0.0),
            cash_before=float(action.get("cash_before") or 0.0),
            cash_after=float(action.get("cash_after") or 0.0),
        )

    def _graph_highlights(self, round_payload: dict[str, Any]) -> GraphStageHighlights:
        actions = self._as_list(round_payload.get("participant_actions"))
        return GraphStageHighlights(
            active_round_id=str(round_payload.get("round_id") or ""),
            active_window=str(round_payload.get("execution_window") or ""),
            active_day_index=int(round_payload.get("day_index") or 0),
            active_trade_date=str(round_payload.get("trade_date") or ""),
            is_incremental_generated=bool(round_payload.get("is_incremental_generated", False)),
            actions_count=int(round_payload.get("actions_count") or len(actions)),
            buy_clone_count=int(round_payload.get("buy_clone_count") or 0),
            sell_clone_count=int(round_payload.get("sell_clone_count") or 0),
            new_entry_clone_count=int(round_payload.get("new_entry_clone_count") or 0),
            exit_clone_count=int(round_payload.get("exit_clone_count") or 0),
            active_clone_ids=self._unique_strings(action.get("participant_id") for action in actions),
            active_symbols=self._unique_strings(action.get("target_symbol") for action in actions),
            dominant_family_ids=self._dominant_families(actions),
            turning_point=bool(round_payload.get("turning_point", False)),
        )

    def _trade_pulse_summary(self, round_payload: dict[str, Any], cards: list[TradeCard]) -> str:
        if not cards:
            return f"第{int(round_payload.get('day_index') or 0)}天暂时没有新增交易动作。"
        fragments = []
        for index, card in enumerate(cards[:3], start=1):
            fragments.append(
                f"{self._clone_alias(card.participant_id, index)}（{self._family_label(card.participant_family)}）"
                f"{self._action_label(card.action_type)}"
            )
        return f"第{int(round_payload.get('day_index') or 0)}天：{'，'.join(fragments)}。"

    def _threshold_summary(self, clone_profile: dict[str, Any], state: dict[str, Any]) -> list[dict[str, Any]]:
        source = state or clone_profile
        rows = [
            ("entry_threshold", source.get("entry_threshold"), "首次进场阈值"),
            ("add_threshold", source.get("add_threshold"), "继续加仓阈值"),
            ("reduce_threshold", source.get("reduce_threshold"), "减仓阈值"),
            ("exit_threshold", source.get("exit_threshold"), "退出阈值"),
            ("cash_available", source.get("cash_available"), "当前可用现金"),
            ("max_event_exposure", source.get("max_event_exposure"), "事件最大风险暴露"),
            ("preferred_execution_windows", source.get("preferred_execution_windows"), "偏好执行窗口"),
            ("avoid_execution_windows", source.get("avoid_execution_windows"), "回避执行窗口"),
        ]
        summary = []
        for metric, value, threshold in rows:
            if value in (None, "", [], {}):
                continue
            summary.append({"metric": metric, "value": value, "threshold": threshold})
        return summary

    def _seen_signals(
        self,
        clone_profile: dict[str, Any],
        state: dict[str, Any],
        action: dict[str, Any],
        incoming: list[dict[str, Any]],
    ) -> list[str]:
        signals: list[str] = []
        signals.extend(str(item) for item in self._items(clone_profile.get("evidence")))
        signals.extend(str(item) for item in self._items(state.get("reason_codes")))
        signals.extend(str(item) for item in self._items(action.get("reason_codes")))
        signals.extend(str(item.get("reason") or "") for item in incoming)
        return self._unique_strings(signals)

    def _family_scoreboard(self, event_id: str, rounds: list[dict[str, Any]]) -> list[dict[str, Any]]:
        participants = {
            str(item.get("participant_id") or ""): item
            for item in self._as_list(self.event_sandbox.load_participants(event_id).get("participants"))
        }
        grouped: dict[str, dict[str, Any]] = defaultdict(
            lambda: {
                "family_id": "",
                "family_label": "",
                "clone_count": 0,
                "active_clone_count": 0,
                "buy_count": 0,
                "sell_count": 0,
                "new_entry_count": 0,
                "exit_count": 0,
                "average_confidence": 0.0,
                "average_authority_weight": 0.0,
                "dominant_symbols": [],
            }
        )
        confidence_samples: dict[str, list[float]] = defaultdict(list)
        authority_samples: dict[str, list[float]] = defaultdict(list)
        symbols: dict[str, set[str]] = defaultdict(set)

        for participant in participants.values():
            family = str(participant.get("participant_family") or "unknown")
            grouped[family]["family_id"] = family
            grouped[family]["family_label"] = self._family_label(family)
            grouped[family]["clone_count"] += 1
            confidence_samples[family].append(float(participant.get("confidence") or 0.0))
            authority_samples[family].append(float(participant.get("authority_weight") or 0.0))

        for round_payload in rounds:
            active_families: set[str] = set()
            for action in self._as_list(round_payload.get("participant_actions")):
                participant_id = str(action.get("participant_id") or "")
                family = str(action.get("participant_family") or participants.get(participant_id, {}).get("participant_family") or "unknown")
                action_name = str(action.get("action_name") or action.get("action_type") or "")
                grouped[family]["family_id"] = family
                grouped[family]["family_label"] = self._family_label(family)
                active_families.add(family)
                if action_name in _BUY_ACTIONS:
                    grouped[family]["buy_count"] += 1
                if action_name in _SELL_ACTIONS:
                    grouped[family]["sell_count"] += 1
                if action_name == "INIT_BUY":
                    grouped[family]["new_entry_count"] += 1
                if action_name == "EXIT":
                    grouped[family]["exit_count"] += 1
                symbol = str(action.get("target_symbol") or "").strip()
                if symbol:
                    symbols[family].add(symbol)
            for family in active_families:
                grouped[family]["active_clone_count"] += 1

        rows = []
        for family, payload in grouped.items():
            confidence = confidence_samples[family]
            authority = authority_samples[family]
            payload["average_confidence"] = round(sum(confidence) / len(confidence), 2) if confidence else 0.0
            payload["average_authority_weight"] = round(sum(authority) / len(authority), 2) if authority else 0.0
            payload["dominant_symbols"] = sorted(symbols[family])
            rows.append(payload)
        return sorted(rows, key=lambda item: (-int(item.get("buy_count") or 0), -int(item.get("active_clone_count") or 0), str(item.get("family_id") or "")))

    def _clone_scoreboard(self, event_id: str, rounds: list[dict[str, Any]]) -> list[dict[str, Any]]:
        clones = {str(item.get("clone_id") or ""): item for item in self._as_list(self.list_clones(event_id).get("clones"))}
        grouped: dict[str, dict[str, Any]] = defaultdict(
            lambda: {
                "clone_id": "",
                "alias": "",
                "participant_family": "",
                "family_label": "",
                "buy_count": 0,
                "sell_count": 0,
                "broadcast_bull_count": 0,
                "broadcast_bear_count": 0,
                "latest_state": "",
                "latest_action": "",
                "net_order_value": 0.0,
            }
        )
        for clone_id, clone in clones.items():
            grouped[clone_id].update(
                {
                    "clone_id": clone_id,
                    "alias": clone.get("alias") or self._clone_alias(clone_id),
                    "participant_family": clone.get("participant_family"),
                    "family_label": clone.get("family_label") or self._family_label(str(clone.get("participant_family") or "")),
                    "latest_state": clone.get("state") or "",
                }
            )

        for round_payload in rounds:
            for action in self._as_list(round_payload.get("participant_actions")):
                clone_id = str(action.get("participant_id") or "")
                action_name = str(action.get("action_name") or action.get("action_type") or "")
                payload = grouped[clone_id]
                payload["clone_id"] = clone_id
                payload["alias"] = payload.get("alias") or self._clone_alias(clone_id)
                payload["participant_family"] = payload.get("participant_family") or action.get("participant_family")
                payload["family_label"] = payload.get("family_label") or self._family_label(str(action.get("participant_family") or ""))
                payload["latest_state"] = action.get("next_state") or payload.get("latest_state") or ""
                payload["latest_action"] = action_name
                if action_name in _BUY_ACTIONS:
                    payload["buy_count"] += 1
                    payload["net_order_value"] += float(action.get("order_value") or 0.0)
                elif action_name in _SELL_ACTIONS:
                    payload["sell_count"] += 1
                    payload["net_order_value"] -= float(action.get("order_value") or 0.0)
                elif action_name == "BROADCAST_BULL":
                    payload["broadcast_bull_count"] += 1
                elif action_name == "BROADCAST_BEAR":
                    payload["broadcast_bear_count"] += 1
        return sorted(grouped.values(), key=lambda item: (-abs(float(item.get("net_order_value") or 0.0)), str(item.get("clone_id") or "")))

    def _regime_scoreboard(self, rounds: list[dict[str, Any]]) -> list[dict[str, Any]]:
        grouped: dict[str, dict[str, Any]] = defaultdict(
            lambda: {"regime_id": "", "label": "", "count": 0, "last_day_index": 0, "last_trade_date": ""}
        )
        for round_payload in rounds:
            regime = str(self._as_dict(round_payload.get("market_state")).get("state") or "unknown")
            grouped[regime]["regime_id"] = regime
            grouped[regime]["label"] = regime
            grouped[regime]["count"] += 1
            grouped[regime]["last_day_index"] = int(round_payload.get("day_index") or 0)
            grouped[regime]["last_trade_date"] = str(round_payload.get("trade_date") or "")
        return sorted(grouped.values(), key=lambda item: (-int(item.get("count") or 0), str(item.get("regime_id") or "")))

    def _failure_taxonomy(self, rounds: list[dict[str, Any]], validation: dict[str, Any]) -> list[dict[str, Any]]:
        if not rounds:
            return [{"failure_id": "no_rounds", "label": "无有效推演", "detail": "当前还没有可用于复盘的交易日。"}]

        latest_market = self._as_dict(rounds[-1].get("market_state"))
        items = []
        state = str(latest_market.get("state") or "").upper()
        if state == "INVALIDATED":
            items.append({"failure_id": "invalidated", "label": "推演失效", "detail": str(latest_market.get("summary") or "风险压力已压过支持链。")})
        elif state == "FRAGILE":
            items.append({"failure_id": "fragile", "label": "路径脆弱", "detail": str(latest_market.get("summary") or "退出链开始放大。")})

        outcomes = self._as_dict(validation.get("outcomes"))
        if str(outcomes.get("status") or "") == "outcome_missing":
            items.append({"failure_id": "outcome_missing", "label": "缺少真实 outcome", "detail": "尚未回填真实 outcome。"})
        if not items:
            items.append({"failure_id": "stable", "label": "当前未触发明显失败模式", "detail": "仍需继续跟踪后续交易日。"})
        return items

    def _transition_summary(self, previous_market: dict[str, Any], current_market: dict[str, Any]) -> str:
        return f"市场状态从 {str(previous_market.get('state') or 'DORMANT')} 切换到 {str(current_market.get('state') or 'UNKNOWN')}。"

    def _dominant_families(self, actions: list[dict[str, Any]]) -> list[str]:
        counts: dict[str, int] = defaultdict(int)
        for action in actions:
            family = str(action.get("participant_family") or "unknown")
            counts[family] += 1
        return [family for family, _ in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:4]]

    def _symbols_for_event(self, event_payload: dict[str, Any]) -> list[str]:
        values = self._items(event_payload["mapping"].get("symbols")) or self._items(event_payload["structure"].get("affected_symbols"))
        return [str(item).strip() for item in values if str(item).strip()]

    def _clone_alias(self, participant_id: str | None, fallback_index: int = 0) -> str:
        raw = str(participant_id or "").strip()
        alpha = "".join(char for char in raw if char.isalpha())
        if alpha:
            return alpha[0].upper()
        if 0 < fallback_index <= 26:
            return chr(64 + fallback_index)
        return raw[:2].upper() or "?"

    def _family_label(self, family: str) -> str:
        key = str(family or "").strip()
        return _FAMILY_LABELS.get(key, key or "参与者")

    def _action_label(self, action_name: str) -> str:
        labels = {
            "INIT_BUY": "首次买入",
            "ADD_BUY": "继续买入",
            "REDUCE": "减仓卖出",
            "EXIT": "退出卖出",
            "BROADCAST_BULL": "看多影响",
            "BROADCAST_BEAR": "看空影响",
            "VALIDATE": "继续验证",
            "WATCH": "继续观察",
            "IGNORE": "保持观望",
        }
        normalized = str(action_name or "").strip().upper()
        return labels.get(normalized, normalized or "执行动作")

    def _capital_range(self, value: Any) -> str:
        amount = float(value or 0.0)
        if amount >= 100_000_000:
            return "100m+"
        if amount >= 50_000_000:
            return "50m-100m"
        if amount >= 20_000_000:
            return "20m-50m"
        if amount >= 5_000_000:
            return "5m-20m"
        return "sub-5m"

    def _as_dict(self, value: Any) -> dict[str, Any]:
        return value if isinstance(value, dict) else {}

    def _as_list(self, value: Any) -> list[dict[str, Any]]:
        return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []

    def _items(self, value: Any) -> list[Any]:
        return list(value) if isinstance(value, list) else []

    def _unique_strings(self, values: Any) -> list[str]:
        seen: set[str] = set()
        results: list[str] = []
        iterable = values if isinstance(values, list) else list(values)
        for item in iterable:
            text = str(item or "").strip()
            if not text or text in seen:
                continue
            seen.add(text)
            results.append(text)
        return results

    def _string(self, value: Any, fallback: str = "") -> str:
        text = str(value or "").strip()
        return text or fallback

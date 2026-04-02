from __future__ import annotations

from dataclasses import asdict
from datetime import date, datetime, timedelta, timezone
import json
from pathlib import Path
from typing import Any

from domain.belief_graph.service import BeliefGraphError, BeliefGraphService
from domain.event_casebook.service import EventCasebookService
from domain.market_world.service import MarketWorldService
from domain.participant_preparation.service import ParticipantPreparationError, ParticipantPreparationService
from domain.scenario_engine.service import ScenarioEngineError, ScenarioEngineService
from domain.simulation_ledger.service import SimulationLedgerService
from domain.event_simulation.timeline import build_simulation_timeline
from schemas.command import TradeCalendarSyncRequest
from schemas.simulation import (
    CN_A_LOT_SIZE,
    DEFAULT_REFERENCE_PRICE,
    DEFAULT_SIMULATION_DAYS,
    MAX_SIMULATION_DAYS,
    SimulationExecutionResult,
    SimulationParticipantState,
    SimulationPrepareResult,
    SimulationRoundPlan,
    SimulationRoundResult,
    SimulationRun,
)
from workflows.event_simulation.graph import build_event_simulation_graph, execute_event_simulation_graph

_LEADER_FAMILIES = {"retail_fast_money", "supply_chain_channel", "media_sentiment"}
_FOLLOWER_FAMILIES = {"institution_confirmation", "industry_research", "quant_risk_budget"}
_RISK_FAMILIES = {"risk_control", "policy_research"}


class EventSimulationError(Exception):
    def __init__(self, *, code: str, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class EventSimulationService:
    def __init__(
        self,
        *,
        runtime_root: Path,
        casebook_service: EventCasebookService,
        participant_preparation: ParticipantPreparationService,
        belief_graph: BeliefGraphService,
        scenario_engine: ScenarioEngineService,
        market_world: MarketWorldService | None = None,
        simulation_ledger: SimulationLedgerService | None = None,
    ) -> None:
        self.runtime_root = runtime_root
        self.casebook_service = casebook_service
        self.participant_preparation = participant_preparation
        self.belief_graph = belief_graph
        self.scenario_engine = scenario_engine
        self.market_world = market_world
        self.simulation_ledger = simulation_ledger
        self.runs_root = runtime_root / "runs"
        self.actions_root = runtime_root / "actions"
        self.snapshots_root = runtime_root / "snapshots"
        self.runs_root.mkdir(parents=True, exist_ok=True)
        self.actions_root.mkdir(parents=True, exist_ok=True)
        self.snapshots_root.mkdir(parents=True, exist_ok=True)

    def prepare_run(self, event_id: str, day_count: int = DEFAULT_SIMULATION_DAYS) -> SimulationPrepareResult:
        casebook = self.casebook_service.load_casebook(event_id)
        if casebook is None:
            raise EventSimulationError(code="EVENT_NOT_FOUND", message="Event casebook not found.", status_code=404)

        try:
            roster_result = self.participant_preparation.prepare_event(event_id)
        except ParticipantPreparationError as exc:
            raise EventSimulationError(code=exc.code, message=exc.message, status_code=exc.status_code) from exc

        try:
            graph_snapshot = self.belief_graph.build_snapshot(event_id)
        except BeliefGraphError as exc:
            raise EventSimulationError(code=exc.code, message=exc.message, status_code=exc.status_code) from exc

        try:
            scenario_result = self.scenario_engine.build_scenarios(event_id)
        except ScenarioEngineError as exc:
            raise EventSimulationError(code=exc.code, message=exc.message, status_code=exc.status_code) from exc

        dominant_scenario = str(scenario_result.dominant_scenario or "").strip()
        if not dominant_scenario:
            raise EventSimulationError(
                code="DOMINANT_SCENARIO_MISSING",
                message="Simulation prepare requires a dominant scenario before execution.",
                status_code=409,
            )
        dominant_case = next(
            (scenario for scenario in scenario_result.scenarios if scenario.scenario_id == dominant_scenario),
            None,
        )
        if dominant_case is None:
            raise EventSimulationError(
                code="SCENARIO_CASE_MISSING",
                message="The dominant scenario could not be resolved from the scenario pack.",
                status_code=409,
            )

        focus_symbol = str((casebook.mapping.get("symbols") or [""])[0] or "")
        reference_price, reference_price_source = self._resolve_reference_price(casebook.mapping, focus_symbol)
        trading_days = self._build_trading_days(
            event_id=event_id,
            anchor_date=self._resolve_anchor_date(casebook.record),
            day_count=self._normalize_day_count(day_count),
        )
        participants = list((roster_result.participant_roster or {}).get("participants") or [])
        participant_states = self._build_participant_states(
            participants=participants,
            graph_snapshot=graph_snapshot,
            dominant_case=dominant_case.to_dict(),
            dominant_scenario=dominant_scenario,
            focus_symbol=focus_symbol,
            reference_price=reference_price,
            lot_size=CN_A_LOT_SIZE,
        )
        rounds = self._build_rounds(
            dominant_scenario=dominant_scenario,
            watchpoints=list(dominant_case.watchpoints),
            graph_status=scenario_result.graph_status,
            trading_days=trading_days,
        )
        execution_clock = self._build_daily_execution_clock(event_id=event_id, trading_days=trading_days)
        run_id = self._next_run_id(event_id)
        simulation_run = SimulationRun(
            run_id=run_id,
            event_id=event_id,
            status="prepared",
            graph_status=scenario_result.graph_status,
            dominant_scenario=dominant_scenario,
            round_count=len(rounds),
            participant_states=participant_states,
            rounds=rounds,
            execution_clock=execution_clock,
            watchpoints=list(dominant_case.watchpoints),
            default_day_count=DEFAULT_SIMULATION_DAYS,
            generated_day_count=len(rounds),
            latest_trade_date=trading_days[-1] if trading_days else "",
            created_at=self._now_iso(),
        )
        self._persist_run(simulation_run)
        runner_payload = {
            "run_id": run_id,
            "event_id": event_id,
            "dominant_scenario": dominant_scenario,
            "graph_status": scenario_result.graph_status,
            "focus_symbols": list(casebook.mapping.get("symbols") or casebook.structure.get("affected_symbols") or []),
            "focus_symbol": focus_symbol,
            "reference_price": reference_price,
            "reference_price_source": reference_price_source,
            "lot_size": CN_A_LOT_SIZE,
            "trading_days": list(trading_days),
            "confirmation_signals": list(casebook.structure.get("monitor_signals") or []),
            "invalidation_conditions": list(dominant_case.invalidation_conditions),
            "watchpoints": list(dominant_case.watchpoints),
            "participant_states": [state.to_dict() for state in participant_states],
            "rounds": [round_plan.to_dict() for round_plan in rounds],
            "execution_clock": execution_clock,
        }
        return SimulationPrepareResult(
            event_id=event_id,
            status="prepared",
            simulation_run=simulation_run.to_dict(),
            runner_payload=runner_payload,
        )

    def run_simulation(self, event_id: str, day_count: int = DEFAULT_SIMULATION_DAYS) -> SimulationExecutionResult:
        prepared = self.prepare_run(event_id, day_count=day_count)
        runner_payload = prepared.runner_payload
        participant_states = [SimulationParticipantState(**item) for item in runner_payload.get("participant_states", [])]
        rounds = [SimulationRoundPlan(**item) for item in runner_payload.get("rounds", [])]
        dominant_scenario = str(runner_payload.get("dominant_scenario") or "")
        graph_status = str(runner_payload.get("graph_status") or "")
        focus_symbols = [str(item) for item in runner_payload.get("focus_symbols", []) if str(item).strip()]
        focus_symbol = str(runner_payload.get("focus_symbol") or (focus_symbols[0] if focus_symbols else ""))
        reference_price = float(runner_payload.get("reference_price") or DEFAULT_REFERENCE_PRICE)
        reference_price_source = str(runner_payload.get("reference_price_source") or "default_demo")
        lot_size = int(runner_payload.get("lot_size") or CN_A_LOT_SIZE)
        graph = build_event_simulation_graph(
            event_id=event_id,
            rounds=rounds,
            dominant_scenario=dominant_scenario,
            graph_status=graph_status,
            focus_symbols=focus_symbols,
        )
        round_results, final_participant_states = execute_event_simulation_graph(
            rounds=rounds,
            participant_states=participant_states,
            dominant_scenario=dominant_scenario,
            graph_status=graph_status,
            focus_symbols=focus_symbols,
            focus_symbol=focus_symbol,
            watchpoints=[str(item) for item in runner_payload.get("watchpoints", []) if str(item).strip()],
            invalidation_conditions=[str(item) for item in runner_payload.get("invalidation_conditions", []) if str(item).strip()],
            confirmation_signals=[str(item) for item in runner_payload.get("confirmation_signals", []) if str(item).strip()],
            reference_price=reference_price,
            reference_price_source=reference_price_source,
            lot_size=lot_size,
        )
        timeline = build_simulation_timeline(round_results)
        run_id = str(prepared.simulation_run.get("run_id") or "")
        if self.simulation_ledger is not None:
            action_log_path, state_snapshots = self.simulation_ledger.persist_round_results(
                event_id=event_id,
                run_id=run_id,
                round_results=round_results,
            )
        else:
            action_log_path = self._persist_action_log(run_id=run_id, round_results=round_results)
            state_snapshots = self._persist_state_snapshots(run_id=run_id, round_results=round_results)

        simulation_run_payload = dict(prepared.simulation_run)
        simulation_run_payload["status"] = "completed"
        simulation_run_payload["graph"] = graph
        simulation_run_payload["participant_states"] = [state.to_dict() for state in final_participant_states]
        simulation_run_payload["round_results"] = [round_result.to_dict() for round_result in round_results]
        simulation_run_payload["timeline"] = timeline.to_dict()
        simulation_run_payload["action_log_path"] = str(action_log_path)
        simulation_run_payload["state_snapshots"] = [str(path) for path in state_snapshots]
        simulation_run_payload["generated_day_count"] = len(round_results)
        simulation_run_payload["latest_trade_date"] = round_results[-1].trade_date if round_results else ""
        simulation_run_payload["completed_at"] = self._now_iso()
        self._persist_run_payload(simulation_run_payload)
        return SimulationExecutionResult(
            event_id=event_id,
            status="completed",
            simulation_run=simulation_run_payload,
            round_results=[round_result.to_dict() for round_result in round_results],
            final_participant_states=[state.to_dict() for state in final_participant_states],
            timeline=timeline.to_dict(),
        )

    def continue_simulation(self, event_id: str) -> SimulationExecutionResult:
        latest_run = self.load_latest_run(event_id)
        if latest_run is None:
            return self.run_simulation(event_id, day_count=DEFAULT_SIMULATION_DAYS)
        current_count = int(
            latest_run.get("generated_day_count")
            or latest_run.get("round_count")
            or len(latest_run.get("round_results") or [])
            or len(latest_run.get("rounds") or [])
            or 0
        )
        next_count = min(MAX_SIMULATION_DAYS, max(DEFAULT_SIMULATION_DAYS, current_count + 1))
        return self.run_simulation(event_id, day_count=next_count)

    def load_latest_run(self, event_id: str) -> dict[str, Any] | None:
        candidates = sorted(self.runs_root.glob(f"{event_id}-run-*.json"))
        if not candidates:
            return None
        return json.loads(candidates[-1].read_text(encoding="utf-8"))

    def _build_participant_states(
        self,
        *,
        participants: list[dict[str, Any]],
        graph_snapshot,
        dominant_case: dict[str, Any],
        dominant_scenario: str,
        focus_symbol: str,
        reference_price: float,
        lot_size: int,
    ) -> list[SimulationParticipantState]:
        first_movers = set(str(item) for item in dominant_case.get("first_movers") or [])
        followers = set(str(item) for item in dominant_case.get("followers") or [])
        participant_states: list[SimulationParticipantState] = []
        for item in participants:
            participant_family = str(item.get("participant_family") or "")
            role = self._role_for(
                participant_family=participant_family,
                clone_index=int(item.get("clone_index") or 0),
                first_movers=first_movers,
                followers=followers,
            )
            current_positions = {
                str(symbol): float(value)
                for symbol, value in dict(item.get("current_positions") or {}).items()
                if str(symbol).strip()
            }
            current_position_quantities = self._position_quantities_from_values(
                current_positions=current_positions,
                focus_symbol=focus_symbol,
                reference_price=reference_price,
                lot_size=lot_size,
            )
            participant_states.append(
                SimulationParticipantState(
                    participant_id=str(item.get("participant_id") or ""),
                    participant_family=participant_family,
                    style_variant=str(item.get("style_variant") or ""),
                    role=role,
                    stance=str(item.get("stance") or "neutral"),
                    authority_weight=float(item.get("authority_weight") or 0.0),
                    confidence=float(item.get("confidence") or 0.0),
                    influence_weight=float(item.get("influence_weight") or 0.0),
                    state=str(item.get("initial_state") or "ready"),
                    capital_bucket=str(item.get("capital_bucket") or ""),
                    capital_base=float(item.get("capital_base") or 0.0),
                    cash_available=float(item.get("cash_available") or 0.0),
                    current_positions=current_positions,
                    current_position_quantities=current_position_quantities,
                    max_event_exposure=float(item.get("max_event_exposure") or 0.0),
                    planned_allocation=self._planned_allocation(item),
                    reaction_latency=int(item.get("reaction_latency") or 0),
                    entry_threshold=float(item.get("entry_threshold") or 0.0),
                    add_threshold=float(item.get("add_threshold") or 0.0),
                    reduce_threshold=float(item.get("reduce_threshold") or 0.0),
                    exit_threshold=float(item.get("exit_threshold") or 0.0),
                    trigger_signals=list(item.get("trigger_conditions") or graph_snapshot.consensus_signals[:3]),
                    invalidation_signals=list(item.get("invalidation_conditions") or graph_snapshot.divergence_signals[:3]),
                    preferred_execution_windows=list(item.get("preferred_execution_windows") or []),
                    avoid_execution_windows=list(item.get("avoid_execution_windows") or []),
                    notes=list(item.get("notes") or []),
                    reason_codes=[
                        f"scenario:{dominant_scenario}",
                        f"role:{role}",
                        f"family:{participant_family}",
                        f"focus_symbol:{focus_symbol or 'market'}",
                    ],
                )
            )
        return participant_states

    def _build_rounds(
        self,
        *,
        dominant_scenario: str,
        watchpoints: list[str],
        graph_status: str,
        trading_days: list[str],
    ) -> list[SimulationRoundPlan]:
        plans: list[SimulationRoundPlan] = []
        focus_map = {
            1: ("Day 1 Seed Ignition", "Let first movers convert the event seed into initial trades."),
            2: ("Day 2 Follow Through", "Let early leaders and followers react to the first trading day."),
            3: ("Day 3 Breadth Expansion", "Watch new participants join while holders reassess conviction."),
            4: ("Day 4 Crowding Test", "Measure crowding, hesitation, and the first serious de-risking signals."),
            5: ("Day 5 Risk Rotation", "Let selling pressure, reducers, and risk guards reshape the chain."),
        }
        for index, trade_date in enumerate(trading_days, start=1):
            focus, objective = focus_map.get(
                index,
                (
                    f"Day {index} Incremental Extension",
                    "Extend the chain by another trading day and observe whether participation persists or fades.",
                ),
            )
            plans.append(
                SimulationRoundPlan(
                    round_id=f"day-{index}",
                    order=index,
                    focus=focus,
                    objective=objective,
                    dominant_scenario=dominant_scenario,
                    execution_window="trading_day",
                    day_index=index,
                    trade_date=trade_date,
                    is_trading_day=True,
                    is_incremental_generated=index > DEFAULT_SIMULATION_DAYS,
                    watchpoints=watchpoints[:3],
                    reason_codes=[
                        f"round:{index}",
                        f"scenario:{dominant_scenario}",
                        f"graph_status:{graph_status}",
                        f"trade_date:{trade_date}",
                    ],
                )
            )
        return plans

    def _build_daily_execution_clock(self, *, event_id: str, trading_days: list[str]) -> dict[str, Any]:
        return {
            "event_id": event_id,
            "current_window": "day_1" if trading_days else "",
            "current_order": 1 if trading_days else 0,
            "status": "ready",
            "windows": [
                {
                    "window_id": f"day_{index}",
                    "label": f"第{index}天",
                    "order": index,
                    "trade_date": trade_date,
                    "description": f"第{index}个交易日 {trade_date} 的完整行为回放。",
                }
                for index, trade_date in enumerate(trading_days, start=1)
            ],
        }

    def _build_trading_days(self, *, event_id: str, anchor_date: date, day_count: int) -> list[str]:
        if self.market_world is not None:
            try:
                horizon = max(21, day_count * 4)
                response = self.market_world.sync_calendar(
                    self.market_world.default_world_id or event_id,
                    TradeCalendarSyncRequest(
                        start_date=anchor_date.isoformat(),
                        end_date=(anchor_date + timedelta(days=horizon)).isoformat(),
                    ),
                )
                trading_days = [day for day in response.trading_days if day >= anchor_date.isoformat()]
                if len(trading_days) >= day_count:
                    return trading_days[:day_count]
            except Exception:
                pass
        trading_days: list[str] = []
        cursor = anchor_date
        while len(trading_days) < day_count:
            if cursor.weekday() < 5:
                trading_days.append(cursor.isoformat())
            cursor += timedelta(days=1)
        return trading_days

    def _resolve_anchor_date(self, record: dict[str, Any]) -> date:
        candidates = [
            str(record.get("event_time") or "").strip(),
            str(record.get("created_at") or "").strip(),
            str(record.get("updated_at") or "").strip(),
        ]
        for candidate in candidates:
            if not candidate:
                continue
            try:
                return date.fromisoformat(candidate[:10])
            except ValueError:
                continue
        return date.today()

    def _resolve_reference_price(self, mapping: dict[str, Any], focus_symbol: str) -> tuple[float, str]:
        reference_prices = dict(mapping.get("reference_prices") or {})
        if focus_symbol and focus_symbol in reference_prices:
            try:
                resolved = float(reference_prices[focus_symbol])
                if resolved > 0:
                    return resolved, "mapping.reference_prices"
            except (TypeError, ValueError):
                pass
        for key in ("reference_price", "demo_reference_price"):
            try:
                resolved = float(mapping.get(key) or 0.0)
                if resolved > 0:
                    return resolved, f"mapping.{key}"
            except (TypeError, ValueError):
                continue
        return DEFAULT_REFERENCE_PRICE, "default_demo"

    def _position_quantities_from_values(
        self,
        *,
        current_positions: dict[str, float],
        focus_symbol: str,
        reference_price: float,
        lot_size: int,
    ) -> dict[str, float]:
        quantities: dict[str, float] = {}
        for symbol, value in current_positions.items():
            if symbol != focus_symbol or reference_price <= 0 or lot_size <= 0:
                quantities[symbol] = 0.0
                continue
            lots = int(max(0.0, float(value)) // (reference_price * lot_size))
            quantities[symbol] = float(lots * lot_size)
        return quantities

    def _normalize_day_count(self, value: int) -> int:
        return max(1, min(MAX_SIMULATION_DAYS, int(value or DEFAULT_SIMULATION_DAYS)))

    def _role_for(
        self,
        *,
        participant_family: str,
        clone_index: int,
        first_movers: set[str],
        followers: set[str],
    ) -> str:
        if participant_family in _RISK_FAMILIES:
            return "risk_guard"
        if participant_family in first_movers or (participant_family in _LEADER_FAMILIES and clone_index <= 2):
            return "leader"
        if participant_family in followers or participant_family in _FOLLOWER_FAMILIES:
            return "follower"
        if participant_family == "media_sentiment":
            return "amplifier"
        return "validator"

    def _planned_allocation(self, participant: dict[str, Any]) -> float:
        capital_base = float(participant.get("capital_base") or 0.0)
        max_event_exposure = float(participant.get("max_event_exposure") or 0.0)
        if capital_base <= 0:
            return 0.0
        return round(min(1.0, max_event_exposure / capital_base), 2)

    def _persist_run(self, simulation_run: SimulationRun) -> None:
        self._persist_run_payload(asdict(simulation_run))

    def _persist_run_payload(self, payload: dict[str, Any]) -> None:
        target_path = self.runs_root / f"{payload['run_id']}.json"
        target_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _persist_action_log(self, *, run_id: str, round_results: list[SimulationRoundResult]) -> Path:
        target_path = self.actions_root / f"{run_id}.jsonl"
        with target_path.open("w", encoding="utf-8") as handle:
            for round_result in round_results:
                for update in round_result.participant_updates:
                    handle.write(
                        json.dumps(
                            {
                                "run_id": run_id,
                                "round_id": round_result.round_id,
                                "order": round_result.order,
                                "day_index": round_result.day_index,
                                "trade_date": round_result.trade_date,
                                "participant_id": update.participant_id,
                                "action_type": update.action_type,
                                "action_name": update.action_name,
                                "target_symbol": update.target_symbol,
                                "order_value": update.order_value,
                                "trade_quantity": update.trade_quantity,
                                "reason_codes": list(update.reason_codes),
                                "state_before": update.previous_state,
                                "state_after": update.next_state,
                            },
                            ensure_ascii=False,
                        )
                        + "\n"
                    )
        return target_path

    def _persist_state_snapshots(self, *, run_id: str, round_results: list[SimulationRoundResult]) -> list[Path]:
        snapshots: list[Path] = []
        for round_result in round_results:
            target_path = self.snapshots_root / f"{run_id}-{round_result.round_id}.json"
            target_path.write_text(
                json.dumps(
                    {
                        "run_id": run_id,
                        "round_id": round_result.round_id,
                        "order": round_result.order,
                        "day_index": round_result.day_index,
                        "trade_date": round_result.trade_date,
                        "participant_states": list(round_result.participant_states),
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            snapshots.append(target_path)
        return snapshots

    def _next_run_id(self, event_id: str) -> str:
        existing = sorted(self.runs_root.glob(f"{event_id}-run-*.json"))
        return f"{event_id}-run-{len(existing) + 1:03d}"

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

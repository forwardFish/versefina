from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
import json
from pathlib import Path

from domain.style_embedding.calibration import build_activation_calibration
from schemas.statements import StatementBehaviorFeatures
from schemas.style import ArchetypeSeed, MarketStyleEmbedding, ParticipantActivationCalibration, ParticipantActivationRule


class StyleEmbeddingError(Exception):
    def __init__(self, *, code: str, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class StyleEmbeddingService:
    def __init__(self, *, trade_record_root: Path, style_root: Path) -> None:
        self.trade_record_root = trade_record_root
        self.style_root = style_root
        self.features_root = style_root / "features"
        self.embeddings_root = style_root / "embeddings"
        self.archetypes_root = style_root / "archetypes"
        self.calibrations_root = style_root / "calibrations"
        for root in (
            self.features_root,
            self.embeddings_root,
            self.archetypes_root,
            self.calibrations_root,
        ):
            root.mkdir(parents=True, exist_ok=True)

    def extract_behavior_features(self, statement_id: str) -> StatementBehaviorFeatures:
        records, source_path = self._load_trade_records(statement_id)
        records = sorted(records, key=lambda item: (str(item.get("traded_at") or ""), int(item.get("row_number") or 0)))
        symbol_sequences = self._group_by_symbol(records)

        holding_days = [self._span_days(items) for items in symbol_sequences.values()]
        avg_holding_days = round(sum(holding_days) / len(holding_days), 2) if holding_days else 0.0
        holding_label = "intraday" if avg_holding_days <= 1 else "swing" if avg_holding_days <= 3 else "position"
        holding_distribution = self._holding_period_distribution(holding_days)

        scale_in_count, scale_out_count = self._scale_counts(records)
        buy_count = sum(1 for item in records if str(item.get("side") or "").lower() == "buy")
        sell_count = sum(1 for item in records if str(item.get("side") or "").lower() == "sell")
        add_reduce_pattern = {
            "label": "scale_in_out" if (scale_in_count + scale_out_count) >= 2 else "one_shot",
            "scale_in_count": scale_in_count,
            "scale_out_count": scale_out_count,
            "buy_count": buy_count,
            "sell_count": sell_count,
        }

        momentum_score, comparable_moves = self._momentum_score(symbol_sequences)
        momentum_label = "momentum_following" if momentum_score >= 0.6 else "mean_reversion" if momentum_score <= 0.4 else "balanced"

        drawdown_tolerance, concentration_score, completed_round_trips = self._risk_profile(records)
        feature_vector = {
            "avg_holding_days": avg_holding_days,
            "scale_in_ratio": self._ratio(scale_in_count, max(buy_count, 1)),
            "scale_out_ratio": self._ratio(scale_out_count, max(sell_count, 1)),
            "momentum_preference_score": momentum_score,
            "drawdown_tolerance_score": float(drawdown_tolerance["score"]),
            "concentration_score": concentration_score,
            "reaction_latency_days": avg_holding_days,
        }

        confidence_notes: list[str] = []
        if len(records) < 4:
            confidence_notes.append("sample_size_below_four")
        if comparable_moves == 0:
            confidence_notes.append("no_comparable_price_ladders")
        if completed_round_trips == 0:
            confidence_notes.append("no_completed_round_trip")
        low_confidence = bool(confidence_notes)
        features = StatementBehaviorFeatures(
            statement_id=statement_id,
            status="partial" if low_confidence else "ready",
            trade_count=len(records),
            source_trade_record_path=str(source_path),
            holding_period={
                "label": holding_label,
                "avg_days": avg_holding_days,
                "distribution": holding_distribution,
            },
            add_reduce_pattern=add_reduce_pattern,
            momentum_preference={
                "label": momentum_label,
                "score": momentum_score,
                "comparable_moves": comparable_moves,
            },
            drawdown_tolerance=drawdown_tolerance,
            feature_vector=feature_vector,
            low_confidence=low_confidence,
            confidence_notes=confidence_notes,
        )
        self._persist(self.features_root, statement_id, asdict(features))
        return features

    def load_behavior_features(self, statement_id: str) -> StatementBehaviorFeatures | None:
        payload = self._load_payload(self.features_root, statement_id)
        return StatementBehaviorFeatures(**payload) if payload is not None else None

    def build_market_style_embedding(self, statement_id: str) -> MarketStyleEmbedding:
        features = self.load_behavior_features(statement_id) or self.extract_behavior_features(statement_id)
        momentum_score = float(features.feature_vector.get("momentum_preference_score") or 0.0)
        avg_holding_days = float(features.feature_vector.get("avg_holding_days") or 0.0)
        embedding = MarketStyleEmbedding(
            statement_id=statement_id,
            status="partial" if features.low_confidence else "ready",
            holding_period_distribution={
                key: float(value)
                for key, value in dict(features.holding_period.get("distribution") or {}).items()
            },
            momentum_preference_score=momentum_score,
            mean_reversion_score=round(1 - momentum_score, 2),
            concentration_score=float(features.feature_vector.get("concentration_score") or 0.0),
            reaction_latency_profile={
                "label": "fast" if avg_holding_days <= 1.5 else "medium" if avg_holding_days <= 3 else "slow",
                "avg_holding_days": avg_holding_days,
                "holding_label": str(features.holding_period.get("label") or ""),
            },
            feature_vector={key: float(value) for key, value in features.feature_vector.items()},
            low_confidence=features.low_confidence,
        )
        self._persist(self.embeddings_root, statement_id, asdict(embedding))
        return embedding

    def load_market_style_embedding(self, statement_id: str) -> MarketStyleEmbedding | None:
        payload = self._load_payload(self.embeddings_root, statement_id)
        return MarketStyleEmbedding(**payload) if payload is not None else None

    def build_archetype_seed(self, statement_id: str) -> ArchetypeSeed:
        embedding = self.load_market_style_embedding(statement_id) or self.build_market_style_embedding(statement_id)
        momentum_score = embedding.momentum_preference_score
        concentration_score = embedding.concentration_score
        latency_label = str(embedding.reaction_latency_profile.get("label") or "")
        if momentum_score >= 0.65 and concentration_score >= 0.45:
            archetype_name = "hot_money_momentum"
            participant_family = "retail_fast_money"
            reaction_rules = [
                "Enter quickly when sector leadership and breadth confirm together.",
                "Scale out once crowding signals appear in later rounds.",
            ]
        elif embedding.mean_reversion_score >= 0.65:
            archetype_name = "institution_mean_reverter"
            participant_family = "institution_confirmation"
            reaction_rules = [
                "Wait for confirmation after the initial shock before allocating.",
                "Prefer staggered adds instead of first-tick chasing.",
            ]
        elif latency_label == "slow":
            archetype_name = "industry_research_rotator"
            participant_family = "industry_research"
            reaction_rules = [
                "Favor deeper follow-through over immediate breakout participation.",
                "Increase conviction only after channel checks and pass-through evidence improve.",
            ]
        else:
            archetype_name = "generic_balanced"
            participant_family = "quant_risk_budget"
            reaction_rules = [
                "Default to balanced risk budgeting until event evidence becomes stronger.",
            ]
        seed = ArchetypeSeed(
            statement_id=statement_id,
            status="partial" if embedding.low_confidence else "ready",
            archetype_name=archetype_name,
            participant_family=participant_family,
            reaction_rules=reaction_rules,
            participant_profile={
                "participant_family": participant_family,
                "activation_bias": embedding.reaction_latency_profile.get("label") or "medium",
                "risk_budget_profile": "tight" if concentration_score >= 0.55 else "balanced",
            },
            confidence=0.35 if embedding.low_confidence else 0.72,
            low_confidence=embedding.low_confidence,
        )
        self._persist(self.archetypes_root, statement_id, asdict(seed))
        return seed

    def load_archetype_seed(self, statement_id: str) -> ArchetypeSeed | None:
        payload = self._load_payload(self.archetypes_root, statement_id)
        return ArchetypeSeed(**payload) if payload is not None else None

    def build_activation_calibration(self, statement_id: str) -> ParticipantActivationCalibration:
        seed = self.load_archetype_seed(statement_id) or self.build_archetype_seed(statement_id)
        calibration = build_activation_calibration(seed)
        self._persist(
            self.calibrations_root,
            statement_id,
            {
                **asdict(calibration),
                "rules": [asdict(rule) for rule in calibration.rules],
            },
        )
        return calibration

    def load_activation_calibration(self, statement_id: str) -> ParticipantActivationCalibration | None:
        payload = self._load_payload(self.calibrations_root, statement_id)
        if payload is None:
            return None
        payload["rules"] = [ParticipantActivationRule(**rule) for rule in payload.get("rules", [])]
        return ParticipantActivationCalibration(**payload)

    def _load_trade_records(self, statement_id: str) -> tuple[list[dict[str, object]], Path]:
        source_path = self.trade_record_root / f"{statement_id}.json"
        if not source_path.exists():
            raise StyleEmbeddingError(
                code="STATEMENT_TRADE_RECORDS_NOT_FOUND",
                message="Trade records must exist before style extraction.",
                status_code=404,
            )
        payload = json.loads(source_path.read_text(encoding="utf-8"))
        if not isinstance(payload, list) or not payload:
            raise StyleEmbeddingError(
                code="STATEMENT_TRADE_RECORDS_EMPTY",
                message="Trade records are empty and cannot produce style features.",
                status_code=400,
            )
        return payload, source_path

    def _group_by_symbol(self, records: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
        grouped: dict[str, list[dict[str, object]]] = {}
        for record in records:
            symbol = str(record.get("symbol") or "").strip()
            grouped.setdefault(symbol, []).append(record)
        return grouped

    def _span_days(self, records: list[dict[str, object]]) -> int:
        days = sorted({str(item.get("traded_at") or "")[:10] for item in records if str(item.get("traded_at") or "")})
        if not days:
            return 0
        start = datetime.fromisoformat(days[0])
        end = datetime.fromisoformat(days[-1])
        return max(1, (end - start).days + 1)

    def _holding_period_distribution(self, holding_days: list[int]) -> dict[str, float]:
        if not holding_days:
            return {"intraday": 0.0, "swing": 0.0, "position": 0.0}
        intraday = sum(1 for item in holding_days if item <= 1)
        swing = sum(1 for item in holding_days if 1 < item <= 3)
        position = sum(1 for item in holding_days if item > 3)
        total = len(holding_days)
        return {
            "intraday": round(intraday / total, 2),
            "swing": round(swing / total, 2),
            "position": round(position / total, 2),
        }

    def _scale_counts(self, records: list[dict[str, object]]) -> tuple[int, int]:
        positions: dict[str, int] = {}
        scale_in_count = 0
        scale_out_count = 0
        for record in records:
            symbol = str(record.get("symbol") or "")
            qty = int(record.get("qty") or 0)
            side = str(record.get("side") or "").lower()
            current_qty = positions.get(symbol, 0)
            if side == "buy" and current_qty > 0:
                scale_in_count += 1
            if side == "sell" and current_qty > qty:
                scale_out_count += 1
            if side == "buy":
                positions[symbol] = current_qty + qty
            else:
                positions[symbol] = max(0, current_qty - qty)
        return scale_in_count, scale_out_count

    def _momentum_score(self, symbol_sequences: dict[str, list[dict[str, object]]]) -> tuple[float, int]:
        momentum_hits = 0
        comparable_moves = 0
        for records in symbol_sequences.values():
            previous_buy_price: float | None = None
            for record in records:
                side = str(record.get("side") or "").lower()
                price = float(record.get("price") or 0.0)
                if side != "buy":
                    continue
                if previous_buy_price is not None:
                    comparable_moves += 1
                    if price >= previous_buy_price:
                        momentum_hits += 1
                previous_buy_price = price
        if comparable_moves == 0:
            return 0.5, 0
        return round(momentum_hits / comparable_moves, 2), comparable_moves

    def _risk_profile(self, records: list[dict[str, object]]) -> tuple[dict[str, object], float, int]:
        positions: dict[str, dict[str, float]] = {}
        symbol_notional: dict[str, float] = {}
        loss_exit_pcts: list[float] = []
        completed_round_trips = 0
        total_notional = 0.0
        for record in records:
            symbol = str(record.get("symbol") or "")
            qty = int(record.get("qty") or 0)
            price = float(record.get("price") or 0.0)
            side = str(record.get("side") or "").lower()
            notional = qty * price
            total_notional += notional
            symbol_notional[symbol] = symbol_notional.get(symbol, 0.0) + notional
            state = positions.setdefault(symbol, {"qty": 0.0, "avg_cost": 0.0})
            if side == "buy":
                new_qty = state["qty"] + qty
                if new_qty > 0:
                    state["avg_cost"] = ((state["avg_cost"] * state["qty"]) + notional) / new_qty
                state["qty"] = new_qty
                continue
            if state["qty"] > 0:
                realized_pct = (price - state["avg_cost"]) / max(state["avg_cost"], 1e-6)
                if realized_pct < 0:
                    loss_exit_pcts.append(realized_pct)
                state["qty"] = max(0.0, state["qty"] - qty)
                if state["qty"] == 0:
                    completed_round_trips += 1
        avg_loss = round(sum(loss_exit_pcts) / len(loss_exit_pcts), 4) if loss_exit_pcts else 0.0
        tolerance_label = "tight" if avg_loss >= -0.02 else "medium" if avg_loss >= -0.05 else "wide"
        tolerance_score = round(min(1.0, abs(avg_loss) / 0.1), 2)
        concentration_score = round(max(symbol_notional.values(), default=0.0) / max(total_notional, 1.0), 2)
        return (
            {
                "label": tolerance_label,
                "score": tolerance_score,
                "avg_realized_loss_pct": avg_loss,
                "loss_exit_count": len(loss_exit_pcts),
            },
            concentration_score,
            completed_round_trips,
        )

    def _persist(self, root: Path, statement_id: str, payload: dict[str, object]) -> None:
        target_path = root / f"{statement_id}.json"
        target_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _load_payload(self, root: Path, statement_id: str) -> dict[str, object] | None:
        target_path = root / f"{statement_id}.json"
        if not target_path.exists():
            return None
        return json.loads(target_path.read_text(encoding="utf-8"))

    def _ratio(self, numerator: float, denominator: float) -> float:
        if denominator <= 0:
            return 0.0
        return round(numerator / denominator, 2)

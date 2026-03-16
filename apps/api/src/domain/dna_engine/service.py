from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
import json
from pathlib import Path

from schemas.agent import TradingAgentProfile
from schemas.command import ProfileGenerationResponse


@dataclass(slots=True)
class DNAEngineService:
    trade_record_root: Path
    profile_root: Path

    def __post_init__(self) -> None:
        self.profile_root.mkdir(parents=True, exist_ok=True)

    def build_profile(self, statement_id: str, *, market: str = "CN_A") -> ProfileGenerationResponse:
        records = self._load_trade_records(statement_id)
        if not records:
            raise FileNotFoundError(f"Trade records for {statement_id} not found.")

        symbol_stats: dict[str, dict[str, float]] = {}
        daily_counts: dict[str, int] = {}
        total_notional = 0.0
        total_cost = 0.0
        buy_count = 0
        sell_count = 0

        for record in records:
            symbol = str(record["symbol"])
            traded_day = str(record["traded_at"])[:10]
            qty = int(record["qty"])
            price = float(record["price"])
            fee = float(record.get("fee", 0.0))
            tax = float(record.get("tax", 0.0))
            notional = qty * price
            total_notional += notional
            total_cost += fee + tax
            daily_counts[traded_day] = daily_counts.get(traded_day, 0) + 1
            bucket = symbol_stats.setdefault(symbol, {"count": 0, "notional": 0.0})
            bucket["count"] += 1
            bucket["notional"] += notional
            if str(record["side"]).lower() == "buy":
                buy_count += 1
            else:
                sell_count += 1

        sorted_symbols = sorted(symbol_stats.items(), key=lambda item: (-item[1]["count"], -item[1]["notional"], item[0]))
        preferred_universe = [{"type": "symbol", "value": symbol} for symbol, _ in sorted_symbols[:3]]
        max_symbol_notional = max((item["notional"] for item in symbol_stats.values()), default=0.0)
        trades_per_day = max(daily_counts.values(), default=1)
        active_days = len(daily_counts)
        turnover_ratio = round(min(0.9, total_notional / max(total_notional, 1.0)), 2)
        fee_pct = round(total_cost / max(total_notional, 1.0), 6)
        max_position_pct = round(min(0.5, max(0.2, max_symbol_notional / max(total_notional, 1.0) + 0.05)), 2)
        max_hold_days = 3 if trades_per_day >= 2 else 5

        style_tags: list[str] = []
        style_tags.append("高换手" if trades_per_day >= 2 else "低频")
        style_tags.append("偏多" if buy_count >= sell_count else "偏卖")
        style_tags.append("集中持仓" if len(symbol_stats) <= 2 else "分散选股")

        profile = TradingAgentProfile(
            statement_id=statement_id,
            market=market,
            styleTags=style_tags,
            preferredUniverse=preferred_universe,
            riskControls={
                "maxPositionPct": max_position_pct,
                "maxHoldDays": max_hold_days,
                "maxDailyTurnoverPct": max(0.2, turnover_ratio),
            },
            cadence={
                "tradesPerDay": trades_per_day,
                "activeDaysPerWeek": min(5, max(1, active_days)),
            },
            costModel={
                "feePct": fee_pct if fee_pct > 0 else 0.0005,
                "slipPct": 0.001,
            },
            decisionPolicy={
                "type": "rule_based",
                "params": {
                    "topSymbols": [symbol for symbol, _ in sorted_symbols[:3]],
                    "activeDays": active_days,
                },
            },
            sourceRuntime="native",
            profileVersion="v1",
            generatedAt=datetime.now().isoformat(),
        )

        profile_path = self.profile_root / f"{statement_id}.json"
        profile_path.write_text(json.dumps(asdict(profile), ensure_ascii=False, indent=2), encoding="utf-8")
        return ProfileGenerationResponse(
            statement_id=statement_id,
            trade_record_count=len(records),
            profile_path=str(profile_path),
            profile=asdict(profile),
        )

    def get_profile(self, statement_id: str) -> dict | None:
        profile_path = self.profile_root / f"{statement_id}.json"
        if not profile_path.exists():
            return None
        return json.loads(profile_path.read_text(encoding="utf-8"))

    def _load_trade_records(self, statement_id: str) -> list[dict]:
        records_path = self.trade_record_root / f"{statement_id}.json"
        if not records_path.exists():
            raise FileNotFoundError(f"Trade records for {statement_id} not found.")
        payload = json.loads(records_path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, list) else []

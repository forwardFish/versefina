from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
import json
from pathlib import Path

from schemas.command import TradeCalendarSyncRequest, TradeCalendarSyncResponse
from schemas.world import WorldSnapshot


_CN_MARKET_HOLIDAYS: dict[int, set[str]] = {
    2026: {
        "2026-01-01",
        "2026-01-02",
        "2026-01-03",
        "2026-02-16",
        "2026-02-17",
        "2026-02-18",
        "2026-02-19",
        "2026-02-20",
        "2026-02-21",
        "2026-04-06",
        "2026-05-01",
        "2026-06-19",
        "2026-09-25",
        "2026-10-01",
        "2026-10-02",
        "2026-10-05",
        "2026-10-06",
        "2026-10-07",
        "2026-10-08",
    }
}


@dataclass(slots=True)
class MarketWorldService:
    default_world_id: str
    runtime_root: Path
    agent_registry_root: Path

    def __post_init__(self) -> None:
        self.runtime_root.mkdir(parents=True, exist_ok=True)

    def sync_calendar(self, world_id: str, payload: TradeCalendarSyncRequest) -> TradeCalendarSyncResponse:
        start = self._parse_date(payload.start_date)
        end = self._parse_date(payload.end_date)
        if end < start:
            raise ValueError("end_date must be greater than or equal to start_date")

        all_days: list[str] = []
        trading_days: list[str] = []
        closed_days: list[str] = []
        current = start
        while current <= end:
            day_text = current.isoformat()
            all_days.append(day_text)
            if self._is_cn_trading_day(current):
                trading_days.append(day_text)
            else:
                closed_days.append(day_text)
            current += timedelta(days=1)

        cache = {
            "world_id": world_id,
            "market": payload.market,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "all_days": all_days,
            "trading_days": trading_days,
            "closed_days": closed_days,
            "source": "fallback_cn_calendar",
            "synced_at": datetime.now().isoformat(),
        }
        cache_path = self._cache_path(world_id)
        cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")

        today = self._resolve_trading_day(trading_days, as_of_date=date.today().isoformat())
        next_day = self._resolve_next_trading_day(trading_days, as_of_date=date.today().isoformat())
        return TradeCalendarSyncResponse(
            world_id=world_id,
            market=payload.market,
            start_date=start.isoformat(),
            end_date=end.isoformat(),
            total_days=len(all_days),
            trading_days=trading_days,
            closed_days=closed_days,
            trading_day=today,
            next_trading_day=next_day,
            source="fallback_cn_calendar",
            cache_path=str(cache_path),
        )

    def panorama(self, *, as_of_date: str | None = None) -> WorldSnapshot:
        return self.snapshot(self.default_world_id, as_of_date=as_of_date)

    def snapshot(self, world_id: str, *, as_of_date: str | None = None) -> WorldSnapshot:
        cache = self._load_cache(world_id)
        trading_days: list[str] = list(cache.get("trading_days") or [])
        trading_day = self._resolve_trading_day(trading_days, as_of_date=as_of_date)
        next_trading_day = self._resolve_next_trading_day(trading_days, as_of_date=as_of_date)
        return WorldSnapshot(
            world_id=world_id,
            market=str(cache.get("market") or "CN_A"),
            trading_day=trading_day or (as_of_date or date.today().isoformat()),
            next_trading_day=next_trading_day,
            total_agents=self._count_agents(),
            market_status="open" if trading_day == (as_of_date or date.today().isoformat()) else "scheduled",
            source=str(cache.get("source") or "fallback_cn_calendar"),
            available_trading_days=trading_days[:20],
        )

    def _load_cache(self, world_id: str) -> dict:
        cache_path = self._cache_path(world_id)
        if cache_path.exists():
            return json.loads(cache_path.read_text(encoding="utf-8"))

        today = date.today()
        default_payload = TradeCalendarSyncRequest(
            start_date=(today - timedelta(days=30)).isoformat(),
            end_date=(today + timedelta(days=60)).isoformat(),
        )
        response = self.sync_calendar(world_id, default_payload)
        return {
            "world_id": response.world_id,
            "market": response.market,
            "start_date": response.start_date,
            "end_date": response.end_date,
            "trading_days": response.trading_days,
            "closed_days": response.closed_days,
            "source": response.source,
        }

    def _cache_path(self, world_id: str) -> Path:
        return self.runtime_root / f"{world_id}.calendar.json"

    def _count_agents(self) -> int:
        if not self.agent_registry_root.exists():
            return 0
        return len(list(self.agent_registry_root.glob("*.json")))

    def _resolve_trading_day(self, trading_days: list[str], *, as_of_date: str | None) -> str | None:
        target = as_of_date or date.today().isoformat()
        if target in trading_days:
            return target
        for trading_day in reversed(trading_days):
            if trading_day < target:
                return trading_day
        return trading_days[0] if trading_days else None

    def _resolve_next_trading_day(self, trading_days: list[str], *, as_of_date: str | None) -> str | None:
        target = as_of_date or date.today().isoformat()
        for trading_day in trading_days:
            if trading_day > target:
                return trading_day
        return None

    def _is_cn_trading_day(self, value: date) -> bool:
        if value.weekday() >= 5:
            return False
        holidays = _CN_MARKET_HOLIDAYS.get(value.year, set())
        return value.isoformat() not in holidays

    def _parse_date(self, value: str) -> date:
        return date.fromisoformat(value)

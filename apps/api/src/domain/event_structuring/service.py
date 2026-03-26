from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path

from schemas.event import EventRecord, EventStructure


_COMMODITY_KEYWORDS: dict[str, tuple[str, str, str, str, float]] = {
    "lithium": ("lithium", "upstream", "battery_materials", "002460.SZ", 0.86),
    "lithium carbonate": ("lithium_carbonate", "upstream", "battery_materials", "002460.SZ", 0.9),
    "copper": ("copper", "upstream", "industrial_metals", "000878.SZ", 0.84),
    "crude oil": ("crude_oil", "upstream", "energy_chemicals", "600028.SH", 0.84),
    "chemical": ("chemical_feedstock", "midstream", "energy_chemicals", "600309.SH", 0.78),
}


class EventStructuringService:
    def __init__(self, runtime_root: Path) -> None:
        self.runtime_root = runtime_root
        self.structure_root = runtime_root / "structures"
        self.structure_root.mkdir(parents=True, exist_ok=True)

    def structure_event(self, record: EventRecord) -> EventStructure:
        normalized_body = record.body.strip()
        commodity, chain_stage, sector, symbol, confidence = self._resolve_mapping(normalized_body)
        trigger_signals = ["spot_price_breakout", "inventory_drawdown", "daily_limit_up_confirmation"]
        structure = EventStructure(
            event_id=record.event_id,
            event_type="supply_chain_price_shock",
            entities=[commodity, sector, symbol],
            commodities=[commodity],
            chain_links=[{"commodity": commodity, "chain_stage": chain_stage, "sector": sector}],
            sectors=[sector],
            affected_symbols=[symbol],
            target_symbols=[symbol],
            causal_chain=[
                f"{commodity} supply tightens",
                f"{chain_stage} cost passes through to {sector}",
                f"{symbol} becomes a first-mover watch target",
            ],
            monitor_signals=trigger_signals,
            trigger_signals=trigger_signals,
            invalidation_conditions=[
                "price shock reverses within 3 sessions",
                "downstream pass-through fails to appear",
            ],
            confidence=confidence,
            summary=normalized_body[:200],
        )
        target_path = self.structure_root / f"{record.event_id}.json"
        target_path.write_text(json.dumps(asdict(structure), ensure_ascii=False, indent=2), encoding="utf-8")
        return structure

    def load_structure(self, event_id: str) -> EventStructure | None:
        target_path = self.structure_root / f"{event_id}.json"
        if not target_path.exists():
            return None
        payload = json.loads(target_path.read_text(encoding="utf-8"))
        return EventStructure(**payload)

    def _resolve_mapping(self, text: str) -> tuple[str, str, str, str, float]:
        lowered = text.lower()
        for keyword, mapping in _COMMODITY_KEYWORDS.items():
            if keyword in lowered:
                return mapping
        return ("supply_chain_price_shock", "upstream", "generic_price_shock", "000001.SZ", 0.55)

from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path

from schemas.event import EventStructure, ThemeMappingResult


_STYLE_TAGS = {
    "battery_materials": ["龙头", "高弹性", "机构票"],
    "energy_chemicals": ["龙头", "高弹性", "情绪票"],
    "generic_price_shock": ["龙头", "补涨候选"],
}


class ThemeMappingService:
    def __init__(self, runtime_root: Path) -> None:
        self.runtime_root = runtime_root
        self.mapping_root = runtime_root / "mappings"
        self.mapping_root.mkdir(parents=True, exist_ok=True)

    def map_structure(self, structure: EventStructure) -> ThemeMappingResult:
        primary_link = structure.chain_links[0] if structure.chain_links else {
            "commodity": "supply_chain_price_shock",
            "chain_stage": "upstream",
            "sector": "generic_price_shock",
        }
        sector = str(primary_link.get("sector") or "generic_price_shock")
        mapping = ThemeMappingResult(
            event_id=structure.event_id,
            commodity=str(primary_link.get("commodity") or "supply_chain_price_shock"),
            chain_stage=str(primary_link.get("chain_stage") or "upstream"),
            sector=sector,
            symbols=list(structure.affected_symbols or []),
            style_tags=list(_STYLE_TAGS.get(sector, ["龙头", "补涨候选"])),
        )
        target_path = self.mapping_root / f"{structure.event_id}.json"
        target_path.write_text(json.dumps(asdict(mapping), ensure_ascii=False, indent=2), encoding="utf-8")
        return mapping

    def load_mapping(self, event_id: str) -> ThemeMappingResult | None:
        target_path = self.mapping_root / f"{event_id}.json"
        if not target_path.exists():
            return None
        payload = json.loads(target_path.read_text(encoding="utf-8"))
        return ThemeMappingResult(**payload)

from __future__ import annotations

from dataclasses import dataclass

from schemas.world import WorldSnapshot


@dataclass(slots=True)
class PanoramaProjection:
    def present(self, panorama: WorldSnapshot) -> WorldSnapshot:
        return panorama

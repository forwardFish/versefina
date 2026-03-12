from __future__ import annotations

from dataclasses import dataclass

from domain.agent_registry.service import AgentRegistryService
from domain.dna_engine.service import DNAEngineService
from domain.market_world.service import MarketWorldService
from domain.platform_control.service import PlatformControlService
from domain.simulation_ledger.service import SimulationLedgerService
from projection.agent_snapshots.service import AgentSnapshotProjection
from projection.panorama.service import PanoramaProjection
from projection.rankings.service import RankingProjection
from settings.base import get_settings


@dataclass(slots=True)
class ServiceContainer:
    agent_registry: AgentRegistryService
    dna_engine: DNAEngineService
    market_world: MarketWorldService
    simulation_ledger: SimulationLedgerService
    platform_control: PlatformControlService
    agent_snapshots: AgentSnapshotProjection
    rankings: RankingProjection
    panorama: PanoramaProjection


def build_container() -> ServiceContainer:
    settings = get_settings()
    return ServiceContainer(
        agent_registry=AgentRegistryService(default_world_id=settings.default_world_id),
        dna_engine=DNAEngineService(),
        market_world=MarketWorldService(default_world_id=settings.default_world_id),
        simulation_ledger=SimulationLedgerService(),
        platform_control=PlatformControlService(),
        agent_snapshots=AgentSnapshotProjection(),
        rankings=RankingProjection(),
        panorama=PanoramaProjection(),
    )

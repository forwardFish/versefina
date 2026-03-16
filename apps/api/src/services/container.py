from __future__ import annotations

from dataclasses import dataclass

from domain.agent_registry.service import AgentRegistryService
from domain.dna_engine.service import DNAEngineService
from domain.market_world.service import MarketWorldService
from domain.platform_control.service import PlatformControlService
from domain.simulation_ledger.service import SimulationLedgerService
from infra.storage.object_store import LocalObjectStore
from modules.statements.parser_service import StatementParseService
from modules.statements.repository import StatementMetadataRepository
from modules.statements.service import StatementIngestionService
from projection.agent_snapshots.service import AgentSnapshotProjection
from projection.panorama.service import PanoramaProjection
from projection.rankings.service import RankingProjection
from settings.base import get_settings
from pathlib import Path


@dataclass(slots=True)
class ServiceContainer:
    agent_registry: AgentRegistryService
    dna_engine: DNAEngineService
    statement_ingestion: StatementIngestionService
    statement_parser: StatementParseService
    market_world: MarketWorldService
    simulation_ledger: SimulationLedgerService
    platform_control: PlatformControlService
    agent_snapshots: AgentSnapshotProjection
    rankings: RankingProjection
    panorama: PanoramaProjection


def build_container() -> ServiceContainer:
    settings = get_settings()
    object_store = LocalObjectStore(
        root=Path(settings.object_store_root),
        bucket=settings.object_store_bucket,
    )
    metadata_repository = StatementMetadataRepository(Path(settings.statement_meta_root))
    statement_ingestion = StatementIngestionService(
        object_store=object_store,
        metadata_repository=metadata_repository,
        max_upload_bytes=settings.statement_max_upload_bytes,
    )
    statement_parser = StatementParseService(
        object_store=object_store,
        parse_report_root=Path(settings.statement_parse_report_root),
        trade_record_root=Path(settings.trade_record_root),
    )
    return ServiceContainer(
        agent_registry=AgentRegistryService(
            default_world_id=settings.default_world_id,
            registry_root=Path(settings.agent_registry_root),
            public_base_url=settings.public_base_url,
        ),
        dna_engine=DNAEngineService(
            trade_record_root=Path(settings.trade_record_root),
            profile_root=Path(settings.agent_profile_root),
        ),
        statement_ingestion=statement_ingestion,
        statement_parser=statement_parser,
        market_world=MarketWorldService(default_world_id=settings.default_world_id),
        simulation_ledger=SimulationLedgerService(),
        platform_control=PlatformControlService(),
        agent_snapshots=AgentSnapshotProjection(),
        rankings=RankingProjection(),
        panorama=PanoramaProjection(),
    )

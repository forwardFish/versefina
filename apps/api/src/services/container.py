from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from domain.acceptance_pack.service import AcceptancePackService
from domain.agent_registry.service import AgentRegistryService
from domain.belief_graph.service import BeliefGraphService
from domain.calibration.service import CalibrationService
from domain.demo_showcase.service import DemoRuntimeShowcaseService
from domain.dna_engine.service import DNAEngineService
from domain.event_casebook.service import EventCasebookService
from domain.finahunt_ingestion.service import FinahuntEventIngestionService
from domain.event_ingestion.service import EventIngestionService
from domain.event_sandbox.service import EventSandboxService
from domain.workbench.service import WorkbenchService
from domain.outcome_review.service import OutcomeReviewService
from domain.reporting.service import ReportingService
from domain.event_structuring.service import EventStructuringService
from domain.event_simulation.service import EventSimulationService
from domain.influence_graph.service import InfluenceGraphService
from domain.market_world.service import MarketWorldService
from domain.platform_control.service import PlatformControlService
from domain.participant_preparation.registry import ParticipantRegistry
from domain.participant_preparation.service import ParticipantPreparationService
from domain.mirror_agent.service import MirrorAgentService
from domain.scenario_engine.service import ScenarioEngineService
from domain.simulation_ledger.service import SimulationLedgerService
from domain.style_embedding.service import StyleEmbeddingService
from domain.theme_mapping.service import ThemeMappingService
from infra.storage.object_store import LocalObjectStore
from modules.statements.parser_service import StatementParseService
from modules.statements.repository import StatementMetadataRepository
from modules.statements.service import StatementIngestionService
from projection.agent_snapshots.service import AgentSnapshotProjection
from projection.event_cards.service import EventCardProjectionService
from projection.panorama.service import PanoramaProjection
from projection.rankings.service import RankingProjection
from settings.base import get_settings


@dataclass(slots=True)
class ServiceContainer:
    acceptance_pack: AcceptancePackService
    agent_registry: AgentRegistryService
    demo_showcase: DemoRuntimeShowcaseService
    dna_engine: DNAEngineService
    statement_ingestion: StatementIngestionService
    statement_parser: StatementParseService
    style_embedding: StyleEmbeddingService
    market_world: MarketWorldService
    simulation_ledger: SimulationLedgerService
    platform_control: PlatformControlService
    event_ingestion: EventIngestionService
    event_structuring: EventStructuringService
    theme_mapping: ThemeMappingService
    event_casebook: EventCasebookService
    finahunt_ingestion: FinahuntEventIngestionService
    participant_registry: ParticipantRegistry
    participant_preparation: ParticipantPreparationService
    belief_graph: BeliefGraphService
    influence_graph: InfluenceGraphService
    scenario_engine: ScenarioEngineService
    mirror_agent: MirrorAgentService
    calibration: CalibrationService
    event_simulation: EventSimulationService
    outcome_review: OutcomeReviewService
    reporting: ReportingService
    event_sandbox: EventSandboxService
    workbench: WorkbenchService
    agent_snapshots: AgentSnapshotProjection
    rankings: RankingProjection
    event_cards: EventCardProjectionService
    panorama: PanoramaProjection


def build_container() -> ServiceContainer:
    settings = get_settings()
    object_store = LocalObjectStore(root=Path(settings.object_store_root), bucket=settings.object_store_bucket)
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
    style_embedding = StyleEmbeddingService(
        trade_record_root=Path(settings.trade_record_root),
        style_root=Path(settings.statement_style_root),
    )
    market_world = MarketWorldService(
        default_world_id=settings.default_world_id,
        runtime_root=Path(settings.market_world_root),
        agent_registry_root=Path(settings.agent_registry_root),
    )
    event_structuring = EventStructuringService(Path(settings.event_runtime_root))
    theme_mapping = ThemeMappingService(Path(settings.event_runtime_root))
    event_casebook = EventCasebookService(Path(settings.event_runtime_root))
    event_ingestion = EventIngestionService(
        runtime_root=Path(settings.event_runtime_root),
        structuring_service=event_structuring,
        theme_mapping_service=theme_mapping,
        casebook_service=event_casebook,
    )
    participant_registry = ParticipantRegistry()
    participant_preparation = ParticipantPreparationService(
        casebook_service=event_casebook,
        participant_registry=participant_registry,
    )
    belief_graph = BeliefGraphService(participant_preparation=participant_preparation)
    influence_graph = InfluenceGraphService()
    scenario_engine = ScenarioEngineService(belief_graph=belief_graph)
    simulation_ledger = SimulationLedgerService(runtime_root=Path(settings.simulation_runtime_root))
    mirror_agent = MirrorAgentService(
        style_root=Path(settings.statement_style_root),
        style_embedding_service=style_embedding,
    )
    calibration = CalibrationService(
        style_root=Path(settings.statement_style_root),
        mirror_agent_service=mirror_agent,
        participant_registry=participant_registry,
        scenario_engine=scenario_engine,
    )
    event_simulation = EventSimulationService(
        runtime_root=Path(settings.simulation_runtime_root),
        casebook_service=event_casebook,
        participant_preparation=participant_preparation,
        belief_graph=belief_graph,
        scenario_engine=scenario_engine,
        market_world=market_world,
        simulation_ledger=simulation_ledger,
    )
    event_cards = EventCardProjectionService(
        casebook_service=event_casebook,
        belief_graph=belief_graph,
        scenario_engine=scenario_engine,
        event_simulation=event_simulation,
    )
    outcome_review = OutcomeReviewService(
        runtime_root=Path(settings.event_runtime_root),
        casebook_service=event_casebook,
        scenario_engine=scenario_engine,
        event_simulation=event_simulation,
    )
    reporting = ReportingService(
        casebook_service=event_casebook,
        belief_graph=belief_graph,
        scenario_engine=scenario_engine,
        event_simulation=event_simulation,
        outcome_review=outcome_review,
        event_cards=event_cards,
    )
    event_sandbox = EventSandboxService(
        runtime_root=Path(settings.event_runtime_root),
        event_ingestion=event_ingestion,
        event_structuring=event_structuring,
        theme_mapping=theme_mapping,
        event_casebook=event_casebook,
        participant_preparation=participant_preparation,
        belief_graph=belief_graph,
        scenario_engine=scenario_engine,
        influence_graph=influence_graph,
        event_simulation=event_simulation,
        reporting=reporting,
        outcome_review=outcome_review,
    )
    finahunt_ingestion = FinahuntEventIngestionService(
        finahunt_runtime_root=Path(settings.finahunt_runtime_root),
        event_runtime_root=Path(settings.event_runtime_root),
        event_ingestion=event_ingestion,
        event_sandbox=event_sandbox,
    )
    workbench = WorkbenchService(
        event_casebook=event_casebook,
        event_ingestion=event_ingestion,
        finahunt_ingestion=finahunt_ingestion,
        event_sandbox=event_sandbox,
    )
    return ServiceContainer(
        acceptance_pack=AcceptancePackService(
            repo_root=Path(settings.roadmap_source_root),
            acceptance_root=Path(settings.roadmap_acceptance_root),
        ),
        agent_registry=AgentRegistryService(
            default_world_id=settings.default_world_id,
            registry_root=Path(settings.agent_registry_root),
            public_base_url=settings.public_base_url,
        ),
        demo_showcase=DemoRuntimeShowcaseService(
            repo_root=Path(settings.roadmap_source_root),
            event_runtime_root=Path(settings.event_runtime_root),
            simulation_runtime_root=Path(settings.simulation_runtime_root),
            statement_meta_root=Path(settings.statement_meta_root),
            statement_parse_report_root=Path(settings.statement_parse_report_root),
            trade_record_root=Path(settings.trade_record_root),
            statement_style_root=Path(settings.statement_style_root),
            roadmap_acceptance_root=Path(settings.roadmap_acceptance_root),
        ),
        dna_engine=DNAEngineService(
            trade_record_root=Path(settings.trade_record_root),
            profile_root=Path(settings.agent_profile_root),
        ),
        statement_ingestion=statement_ingestion,
        statement_parser=statement_parser,
        style_embedding=style_embedding,
        market_world=market_world,
        simulation_ledger=simulation_ledger,
        platform_control=PlatformControlService(),
        event_ingestion=event_ingestion,
        event_structuring=event_structuring,
        theme_mapping=theme_mapping,
        event_casebook=event_casebook,
        finahunt_ingestion=finahunt_ingestion,
        participant_registry=participant_registry,
        participant_preparation=participant_preparation,
        belief_graph=belief_graph,
        influence_graph=influence_graph,
        scenario_engine=scenario_engine,
        mirror_agent=mirror_agent,
        calibration=calibration,
        event_simulation=event_simulation,
        outcome_review=outcome_review,
        reporting=reporting,
        event_sandbox=event_sandbox,
        workbench=workbench,
        agent_snapshots=AgentSnapshotProjection(),
        rankings=RankingProjection(),
        event_cards=event_cards,
        panorama=PanoramaProjection(),
    )

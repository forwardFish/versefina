from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class StatementUploadRequest:
    owner_id: str
    file_name: str
    content_type: str
    byte_size: int
    market: str = "CN_A"
    statement_id: str | None = None


@dataclass(frozen=True, slots=True)
class StatementUploadResponse:
    statement_id: str
    upload_status: str
    object_key: str | None
    bucket: str
    file_name: str
    byte_size: int
    market: str
    error_code: str | None = None
    error_message: str | None = None


@dataclass(frozen=True, slots=True)
class StatementStatusUpdateRequest:
    next_status: str
    error_code: str | None = None
    error_message: str | None = None


@dataclass(frozen=True, slots=True)
class StatementParseResponse:
    statement_id: str
    upload_status: str
    parsed_records: int
    failed_records: int
    parse_report_path: str
    trade_record_path: str
    error_code: str | None = None
    error_message: str | None = None


@dataclass(frozen=True, slots=True)
class ProfileGenerationResponse:
    statement_id: str
    trade_record_count: int
    profile_path: str
    profile: dict[str, Any]


@dataclass(frozen=True, slots=True)
class AgentCreateRequest:
    owner_id: str
    statement_id: str
    init_cash: float
    agent_id: str | None = None
    source_runtime: str = "native"
    world_id: str | None = None


@dataclass(frozen=True, slots=True)
class AgentCreateResponse:
    agent_id: str
    owner_id: str
    statement_id: str
    world_id: str
    status: str
    init_cash: float
    public_url: str
    profile_path: str
    source_runtime: str
    created_at: str


@dataclass(frozen=True, slots=True)
class StatementMetadata:
    statement_id: str
    owner_id: str
    market: str
    file_name: str
    content_type: str
    detected_file_type: str
    parser_key: str
    byte_size: int
    bucket: str
    object_key: str
    upload_status: str
    created_at: str
    updated_at: str
    error_code: str | None = None
    error_message: str | None = None


@dataclass(frozen=True, slots=True)
class AgentRegisterRequest:
    agent_id: str
    owner_id: str
    source_runtime: str = "platform"


@dataclass(frozen=True, slots=True)
class HeartbeatRequest:
    heartbeat_at: str
    status: str = "ACTIVE"


@dataclass(frozen=True, slots=True)
class SubmitActionRequest:
    agent_id: str
    world_id: str
    actions: list[dict[str, str]] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class TradeCalendarSyncRequest:
    start_date: str
    end_date: str
    market: str = "CN_A"


@dataclass(frozen=True, slots=True)
class TradeCalendarSyncResponse:
    world_id: str
    market: str
    start_date: str
    end_date: str
    total_days: int
    trading_days: list[str]
    closed_days: list[str]
    trading_day: str | None
    next_trading_day: str | None
    source: str
    cache_path: str


@dataclass(frozen=True, slots=True)
class EventCreateRequest:
    title: str
    body: str
    source: str = "manual_text"
    event_time: str | None = None


@dataclass(frozen=True, slots=True)
class EventCreateResponse:
    event_id: str
    event_type: str
    status: str
    structure: dict[str, Any]
    mapping: dict[str, Any]


@dataclass(frozen=True, slots=True)
class EventPrepareResponse:
    event_id: str
    status: str
    casebook: dict[str, Any]
    participant_roster: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class FinahuntEventImportRequest:
    run_id: str | None = None
    rank_position: int | None = None
    message_id: str | None = None
    auto_structure_prepare_simulate: bool = True


@dataclass(frozen=True, slots=True)
class FinahuntEventImportResponse:
    event_id: str
    status: str
    run_id: str
    source_event_id: str
    lineage: dict[str, Any]
    structure_status: str
    participant_status: str
    simulation_status: str


@dataclass(frozen=True, slots=True)
class OutcomeReviewWriteRequest:
    horizon: str
    sector_performance: str
    leader_performance: str
    expansion_status: str
    sentiment_status: str
    analyst_note: str = ""
    supporting_evidence: list[str] = field(default_factory=list)

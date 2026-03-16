from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]


@dataclass(frozen=True, slots=True)
class Settings:
    app_name: str = "versefina-api"
    environment: str = "development"
    default_world_id: str = "cn-a"
    read_model_source: str = "projection"
    public_base_url: str = "http://127.0.0.1:8000"
    object_store_bucket: str = "versefina-artifacts"
    object_store_root: str = str(REPO_ROOT / ".runtime" / "object_store")
    statement_meta_root: str = str(REPO_ROOT / ".runtime" / "statement_meta")
    statement_parse_report_root: str = str(REPO_ROOT / ".runtime" / "statement_parse_reports")
    trade_record_root: str = str(REPO_ROOT / ".runtime" / "trade_records")
    agent_profile_root: str = str(REPO_ROOT / ".runtime" / "agent_profiles")
    agent_registry_root: str = str(REPO_ROOT / ".runtime" / "agents")
    statement_max_upload_bytes: int = 10 * 1024 * 1024


def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "versefina-api"),
        environment=os.getenv("ENVIRONMENT", "development"),
        default_world_id=os.getenv("DEFAULT_WORLD_ID", "cn-a"),
        read_model_source=os.getenv("READ_MODEL_SOURCE", "projection"),
        public_base_url=os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8000"),
        object_store_bucket=os.getenv("OBJECT_STORE_BUCKET", "versefina-artifacts"),
        object_store_root=os.getenv("OBJECT_STORE_ROOT", str(REPO_ROOT / ".runtime" / "object_store")),
        statement_meta_root=os.getenv("STATEMENT_META_ROOT", str(REPO_ROOT / ".runtime" / "statement_meta")),
        statement_parse_report_root=os.getenv(
            "STATEMENT_PARSE_REPORT_ROOT",
            str(REPO_ROOT / ".runtime" / "statement_parse_reports"),
        ),
        trade_record_root=os.getenv("TRADE_RECORD_ROOT", str(REPO_ROOT / ".runtime" / "trade_records")),
        agent_profile_root=os.getenv("AGENT_PROFILE_ROOT", str(REPO_ROOT / ".runtime" / "agent_profiles")),
        agent_registry_root=os.getenv("AGENT_REGISTRY_ROOT", str(REPO_ROOT / ".runtime" / "agents")),
        statement_max_upload_bytes=int(os.getenv("STATEMENT_MAX_UPLOAD_BYTES", str(10 * 1024 * 1024))),
    )

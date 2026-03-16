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
    object_store_bucket: str = "versefina-artifacts"
    object_store_root: str = str(REPO_ROOT / ".runtime" / "object_store")
    statement_meta_root: str = str(REPO_ROOT / ".runtime" / "statement_meta")
    statement_max_upload_bytes: int = 10 * 1024 * 1024


def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "versefina-api"),
        environment=os.getenv("ENVIRONMENT", "development"),
        default_world_id=os.getenv("DEFAULT_WORLD_ID", "cn-a"),
        read_model_source=os.getenv("READ_MODEL_SOURCE", "projection"),
        object_store_bucket=os.getenv("OBJECT_STORE_BUCKET", "versefina-artifacts"),
        object_store_root=os.getenv("OBJECT_STORE_ROOT", str(REPO_ROOT / ".runtime" / "object_store")),
        statement_meta_root=os.getenv("STATEMENT_META_ROOT", str(REPO_ROOT / ".runtime" / "statement_meta")),
        statement_max_upload_bytes=int(os.getenv("STATEMENT_MAX_UPLOAD_BYTES", str(10 * 1024 * 1024))),
    )

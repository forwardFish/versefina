from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    app_name: str = "versefina-api"
    environment: str = "development"
    default_world_id: str = "cn-a"
    read_model_source: str = "projection"


def get_settings() -> Settings:
    return Settings()

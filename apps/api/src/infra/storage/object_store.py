from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from settings.base import get_settings


@dataclass(frozen=True, slots=True)
class StoredObject:
    bucket: str
    object_key: str
    absolute_path: str


def object_store_bucket() -> str:
    return get_settings().object_store_bucket


def object_store_root() -> Path:
    return Path(get_settings().object_store_root)


def build_statement_object_key(owner_id: str, statement_id: str, file_name: str) -> str:
    safe_name = Path(file_name).name
    return f"statements/{owner_id}/{statement_id}/{safe_name}"


class LocalObjectStore:
    def __init__(self, *, root: Path | None = None, bucket: str | None = None) -> None:
        self.root = root or object_store_root()
        self.bucket = bucket or object_store_bucket()

    def put_bytes(self, *, object_key: str, data: bytes) -> StoredObject:
        target = self.root / self.bucket / Path(object_key)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        return StoredObject(bucket=self.bucket, object_key=object_key, absolute_path=str(target))

    def delete(self, *, object_key: str) -> None:
        target = self.root / self.bucket / Path(object_key)
        if target.exists():
            target.unlink()
            self._prune_empty_parents(target.parent)

    def exists(self, *, object_key: str) -> bool:
        return (self.root / self.bucket / Path(object_key)).exists()

    def _prune_empty_parents(self, start: Path) -> None:
        boundary = self.root / self.bucket
        current = start
        while current != boundary and current.exists():
            try:
                current.rmdir()
            except OSError:
                break
            current = current.parent

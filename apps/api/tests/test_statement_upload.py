from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from app import create_app
from infra.storage.object_store import LocalObjectStore
from modules.statements.repository import StatementMetadataRepository
from modules.statements.status_machine import (
    InvalidStatementTransitionError,
    STATEMENT_STATUS_FAILED,
    STATEMENT_STATUS_PARSING,
    STATEMENT_STATUS_UPLOADED,
    validate_statement_transition,
)


class StatementUploadApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.object_store_root = Path(self.tempdir.name) / "object_store"
        self.statement_meta_root = Path(self.tempdir.name) / "statement_meta"
        self.original_env = {
            "OBJECT_STORE_ROOT": os.environ.get("OBJECT_STORE_ROOT"),
            "STATEMENT_META_ROOT": os.environ.get("STATEMENT_META_ROOT"),
            "OBJECT_STORE_BUCKET": os.environ.get("OBJECT_STORE_BUCKET"),
            "STATEMENT_MAX_UPLOAD_BYTES": os.environ.get("STATEMENT_MAX_UPLOAD_BYTES"),
        }
        os.environ["OBJECT_STORE_ROOT"] = str(self.object_store_root)
        os.environ["STATEMENT_META_ROOT"] = str(self.statement_meta_root)
        os.environ["OBJECT_STORE_BUCKET"] = "test-artifacts"
        os.environ["STATEMENT_MAX_UPLOAD_BYTES"] = str(10 * 1024 * 1024)
        self.client = TestClient(create_app())

    def tearDown(self) -> None:
        self.client.close()
        for key, value in self.original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        self.tempdir.cleanup()

    def test_multipart_upload_persists_file_and_metadata(self) -> None:
        response = self.client.post(
            "/api/v1/statements/upload",
            data={"owner_id": "user_123", "market": "CN_A", "statement_id": "stmt_demo_001"},
            files={"file": ("demo.csv", b"ts_code,side,qty\n600519.SH,buy,100\n", "text/csv")},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["upload_status"], "uploaded")
        self.assertEqual(payload["statement_id"], "stmt_demo_001")
        self.assertEqual(payload["bucket"], "test-artifacts")
        stored_path = self.object_store_root / "test-artifacts" / "statements" / "user_123" / "stmt_demo_001" / "demo.csv"
        self.assertTrue(stored_path.exists())
        metadata_path = self.statement_meta_root / "stmt_demo_001.json"
        self.assertTrue(metadata_path.exists())
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        self.assertEqual(metadata["upload_status"], "uploaded")
        self.assertEqual(metadata["object_key"], "statements/user_123/stmt_demo_001/demo.csv")
        self.assertEqual(metadata["detected_file_type"], "csv")
        self.assertEqual(metadata["parser_key"], "statement_csv_parser")

        detail_response = self.client.get("/api/v1/statements/stmt_demo_001")
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.json()["upload_status"], "uploaded")

    def test_upload_rejects_invalid_extension(self) -> None:
        response = self.client.post(
            "/api/v1/statements/upload",
            data={"owner_id": "user_123", "market": "CN_A"},
            files={"file": ("demo.txt", b"not a statement", "text/plain")},
        )
        self.assertEqual(response.status_code, 400)
        payload = response.json()
        self.assertEqual(payload["upload_status"], "rejected")
        self.assertEqual(payload["error_code"], "STATEMENT_FILE_TYPE_UNSUPPORTED")

    def test_upload_rejects_content_type_mismatch(self) -> None:
        response = self.client.post(
            "/api/v1/statements/upload",
            data={"owner_id": "user_123", "market": "CN_A"},
            files={"file": ("demo.csv", b"ts_code,side,qty\n600519.SH,buy,100\n", "application/pdf")},
        )
        self.assertEqual(response.status_code, 400)
        payload = response.json()
        self.assertEqual(payload["upload_status"], "rejected")
        self.assertEqual(payload["error_code"], "STATEMENT_FILE_TYPE_MISMATCH")

    def test_upload_rejects_oversized_file(self) -> None:
        response = self.client.post(
            "/api/v1/statements/upload",
            data={"owner_id": "user_123", "market": "CN_A"},
            files={"file": ("demo.csv", b"a" * (10 * 1024 * 1024 + 1), "text/csv")},
        )
        self.assertEqual(response.status_code, 400)
        payload = response.json()
        self.assertEqual(payload["upload_status"], "rejected")
        self.assertEqual(payload["error_code"], "STATEMENT_FILE_TOO_LARGE")

    def test_statement_status_transition_roundtrip(self) -> None:
        upload_response = self.client.post(
            "/api/v1/statements/upload",
            data={"owner_id": "user_123", "market": "CN_A", "statement_id": "stmt_demo_002"},
            files={"file": ("demo.csv", b"ts_code,side,qty\n600519.SH,buy,100\n", "text/csv")},
        )
        self.assertEqual(upload_response.status_code, 200)

        parsing_response = self.client.post(
            "/api/v1/statements/stmt_demo_002/status",
            json={"next_status": "parsing"},
        )
        self.assertEqual(parsing_response.status_code, 200)
        self.assertEqual(parsing_response.json()["upload_status"], "parsing")

        parsed_response = self.client.post(
            "/api/v1/statements/stmt_demo_002/status",
            json={"next_status": "parsed"},
        )
        self.assertEqual(parsed_response.status_code, 200)
        self.assertEqual(parsed_response.json()["upload_status"], "parsed")

        invalid_response = self.client.post(
            "/api/v1/statements/stmt_demo_002/status",
            json={"next_status": "uploaded"},
        )
        self.assertEqual(invalid_response.status_code, 400)
        self.assertEqual(invalid_response.json()["error_code"], "STATEMENT_INVALID_TRANSITION")

    def test_upload_rolls_back_when_object_store_write_fails(self) -> None:
        class FailingObjectStore(LocalObjectStore):
            def put_bytes(self, *, object_key: str, data: bytes):  # type: ignore[override]
                raise OSError("disk unavailable")

        app = create_app()
        app.state.container.statement_ingestion.object_store = FailingObjectStore(
            root=self.object_store_root,
            bucket="test-artifacts",
        )
        client = TestClient(app)
        try:
            response = client.post(
                "/api/v1/statements/upload",
                data={"owner_id": "user_123", "market": "CN_A", "statement_id": "stmt_store_fail"},
                files={"file": ("demo.csv", b"ts_code,side,qty\n600519.SH,buy,100\n", "text/csv")},
            )
            self.assertEqual(response.status_code, 500)
            payload = response.json()
            self.assertEqual(payload["error_code"], "STATEMENT_STORAGE_WRITE_FAILED")
            self.assertFalse((self.statement_meta_root / "stmt_store_fail.json").exists())
        finally:
            client.close()

    def test_upload_rolls_back_object_when_metadata_persist_fails(self) -> None:
        class FailingMetadataRepository(StatementMetadataRepository):
            def save(self, metadata):  # type: ignore[override]
                raise OSError("metadata store unavailable")

        app = create_app()
        app.state.container.statement_ingestion.metadata_repository = FailingMetadataRepository(self.statement_meta_root)
        client = TestClient(app)
        stored_path = self.object_store_root / "test-artifacts" / "statements" / "user_123" / "stmt_meta_fail" / "demo.csv"
        try:
            response = client.post(
                "/api/v1/statements/upload",
                data={"owner_id": "user_123", "market": "CN_A", "statement_id": "stmt_meta_fail"},
                files={"file": ("demo.csv", b"ts_code,side,qty\n600519.SH,buy,100\n", "text/csv")},
            )
            self.assertEqual(response.status_code, 500)
            payload = response.json()
            self.assertEqual(payload["error_code"], "STATEMENT_METADATA_PERSIST_FAILED")
            self.assertFalse(stored_path.exists())
            self.assertFalse((self.statement_meta_root / "stmt_meta_fail.json").exists())
        finally:
            client.close()


class StatementStatusMachineTestCase(unittest.TestCase):
    def test_allows_uploaded_to_parsing(self) -> None:
        validate_statement_transition(STATEMENT_STATUS_UPLOADED, STATEMENT_STATUS_PARSING)

    def test_blocks_failed_to_uploaded(self) -> None:
        with self.assertRaises(InvalidStatementTransitionError):
            validate_statement_transition(STATEMENT_STATUS_FAILED, STATEMENT_STATUS_UPLOADED)


if __name__ == "__main__":
    unittest.main()

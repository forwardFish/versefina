from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd
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
        self.statement_parse_report_root = Path(self.tempdir.name) / "statement_parse_reports"
        self.trade_record_root = Path(self.tempdir.name) / "trade_records"
        self.agent_profile_root = Path(self.tempdir.name) / "agent_profiles"
        self.agent_registry_root = Path(self.tempdir.name) / "agents"
        self.original_env = {
            "OBJECT_STORE_ROOT": os.environ.get("OBJECT_STORE_ROOT"),
            "STATEMENT_META_ROOT": os.environ.get("STATEMENT_META_ROOT"),
            "STATEMENT_PARSE_REPORT_ROOT": os.environ.get("STATEMENT_PARSE_REPORT_ROOT"),
            "TRADE_RECORD_ROOT": os.environ.get("TRADE_RECORD_ROOT"),
            "AGENT_PROFILE_ROOT": os.environ.get("AGENT_PROFILE_ROOT"),
            "AGENT_REGISTRY_ROOT": os.environ.get("AGENT_REGISTRY_ROOT"),
            "PUBLIC_BASE_URL": os.environ.get("PUBLIC_BASE_URL"),
            "OBJECT_STORE_BUCKET": os.environ.get("OBJECT_STORE_BUCKET"),
            "STATEMENT_MAX_UPLOAD_BYTES": os.environ.get("STATEMENT_MAX_UPLOAD_BYTES"),
        }
        os.environ["OBJECT_STORE_ROOT"] = str(self.object_store_root)
        os.environ["STATEMENT_META_ROOT"] = str(self.statement_meta_root)
        os.environ["STATEMENT_PARSE_REPORT_ROOT"] = str(self.statement_parse_report_root)
        os.environ["TRADE_RECORD_ROOT"] = str(self.trade_record_root)
        os.environ["AGENT_PROFILE_ROOT"] = str(self.agent_profile_root)
        os.environ["AGENT_REGISTRY_ROOT"] = str(self.agent_registry_root)
        os.environ["PUBLIC_BASE_URL"] = "http://127.0.0.1:8000"
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

    def test_parse_csv_statement_generates_trade_records_and_report(self) -> None:
        upload_response = self.client.post(
            "/api/v1/statements/upload",
            data={"owner_id": "user_123", "market": "CN_A", "statement_id": "stmt_parse_csv"},
            files={
                "file": (
                    "broker_cn.csv",
                    "成交日期,证券代码,买卖方向,成交数量,成交价格,手续费,印花税\n2026-03-14,600519.SH,买入,100,1700.5,5,0\n",
                    "text/csv",
                )
            },
        )
        self.assertEqual(upload_response.status_code, 200)

        parse_response = self.client.post("/api/v1/statements/stmt_parse_csv/parse")
        self.assertEqual(parse_response.status_code, 200)
        payload = parse_response.json()
        self.assertEqual(payload["final_status"], "parsed")
        self.assertEqual(payload["parsed_records"], 1)
        self.assertEqual(payload["failed_records"], 0)

        records_path = self.trade_record_root / "stmt_parse_csv.json"
        report_path = self.statement_parse_report_root / "stmt_parse_csv.json"
        self.assertTrue(records_path.exists())
        self.assertTrue(report_path.exists())
        records = json.loads(records_path.read_text(encoding="utf-8"))
        self.assertEqual(records[0]["side"], "buy")
        self.assertEqual(records[0]["symbol"], "600519.SH")
        self.assertEqual(records[0]["qty"], 100)

        report_response = self.client.get("/api/v1/statements/stmt_parse_csv/parse-report")
        self.assertEqual(report_response.status_code, 200)
        self.assertEqual(report_response.json()["parsed_records"], 1)

    def test_parse_english_columns_supported(self) -> None:
        upload_response = self.client.post(
            "/api/v1/statements/upload",
            data={"owner_id": "user_123", "market": "CN_A", "statement_id": "stmt_parse_en"},
            files={
                "file": (
                    "broker_en.csv",
                    "trade_date,symbol,side,quantity,price,fee,tax\n2026-03-14,300750.SZ,sell,200,198.1,6.5,1\n",
                    "text/csv",
                )
            },
        )
        self.assertEqual(upload_response.status_code, 200)
        parse_response = self.client.post("/api/v1/statements/stmt_parse_en/parse")
        self.assertEqual(parse_response.status_code, 200)
        payload = parse_response.json()
        self.assertEqual(payload["final_status"], "parsed")
        records = json.loads((self.trade_record_root / "stmt_parse_en.json").read_text(encoding="utf-8"))
        self.assertEqual(records[0]["side"], "sell")
        self.assertEqual(records[0]["price"], 198.1)

    def test_parse_xlsx_statement_generates_trade_records(self) -> None:
        buffer = io.BytesIO()
        frame = pd.DataFrame(
            [
                {
                    "trade_date": "2026-03-14",
                    "symbol": "300750.SZ",
                    "side": "buy",
                    "quantity": 100,
                    "price": 201.8,
                    "fee": 6.0,
                    "tax": 0.0,
                }
            ]
        )
        frame.to_excel(buffer, index=False)
        buffer.seek(0)

        upload_response = self.client.post(
            "/api/v1/statements/upload",
            data={"owner_id": "user_123", "market": "CN_A", "statement_id": "stmt_parse_xlsx"},
            files={
                "file": (
                    "broker.xlsx",
                    buffer.getvalue(),
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            },
        )
        self.assertEqual(upload_response.status_code, 200)

        parse_response = self.client.post("/api/v1/statements/stmt_parse_xlsx/parse")
        self.assertEqual(parse_response.status_code, 200)
        payload = parse_response.json()
        self.assertEqual(payload["final_status"], "parsed")
        self.assertEqual(payload["parsed_records"], 1)

    def test_parse_missing_mapping_rule_transitions_to_failed(self) -> None:
        upload_response = self.client.post(
            "/api/v1/statements/upload",
            data={"owner_id": "user_123", "market": "CN_A", "statement_id": "stmt_parse_fail"},
            files={
                "file": (
                    "unknown.csv",
                    "foo,bar,baz\n1,2,3\n",
                    "text/csv",
                )
            },
        )
        self.assertEqual(upload_response.status_code, 200)
        parse_response = self.client.post("/api/v1/statements/stmt_parse_fail/parse")
        self.assertEqual(parse_response.status_code, 400)
        payload = parse_response.json()
        self.assertEqual(payload["error_code"], "STATEMENT_MAPPING_RULE_NOT_FOUND")

        detail_response = self.client.get("/api/v1/statements/stmt_parse_fail")
        self.assertEqual(detail_response.status_code, 200)
        detail_payload = detail_response.json()
        self.assertEqual(detail_payload["upload_status"], "failed")
        self.assertEqual(detail_payload["error_code"], "STATEMENT_MAPPING_RULE_NOT_FOUND")

    def test_profile_generation_persists_profile_json(self) -> None:
        upload_response = self.client.post(
            "/api/v1/statements/upload",
            data={"owner_id": "user_profile", "market": "CN_A", "statement_id": "stmt_profile_001"},
            files={
                "file": (
                    "profile.csv",
                    "trade_date,symbol,side,quantity,price,fee,tax\n"
                    "2026-03-14,600519.SH,buy,100,1700.5,5,0\n"
                    "2026-03-15,300750.SZ,sell,200,198.1,6.5,1\n",
                    "text/csv",
                )
            },
        )
        self.assertEqual(upload_response.status_code, 200)
        self.assertEqual(self.client.post("/api/v1/statements/stmt_profile_001/parse").status_code, 200)

        profile_response = self.client.post("/api/v1/statements/stmt_profile_001/profile")
        self.assertEqual(profile_response.status_code, 200)
        payload = profile_response.json()
        self.assertEqual(payload["statement_id"], "stmt_profile_001")
        self.assertEqual(payload["trade_record_count"], 2)
        self.assertIn("styleTags", payload["profile"])
        self.assertIn("riskControls", payload["profile"])
        self.assertTrue((self.agent_profile_root / "stmt_profile_001.json").exists())

        query_response = self.client.get("/api/v1/statements/stmt_profile_001/profile")
        self.assertEqual(query_response.status_code, 200)
        self.assertEqual(query_response.json()["statement_id"], "stmt_profile_001")

    def test_agent_creation_closes_statement_to_agent_loop(self) -> None:
        upload_response = self.client.post(
            "/api/v1/statements/upload",
            data={"owner_id": "user_agent", "market": "CN_A", "statement_id": "stmt_agent_001"},
            files={
                "file": (
                    "agent.csv",
                    "trade_date,symbol,side,quantity,price,fee,tax\n"
                    "2026-03-14,600519.SH,buy,100,1700.5,5,0\n"
                    "2026-03-15,600519.SH,sell,100,1710.5,5,1\n",
                    "text/csv",
                )
            },
        )
        self.assertEqual(upload_response.status_code, 200)
        self.assertEqual(self.client.post("/api/v1/statements/stmt_agent_001/parse").status_code, 200)
        self.assertEqual(self.client.post("/api/v1/statements/stmt_agent_001/profile").status_code, 200)

        create_response = self.client.post(
            "/api/v1/agents",
            json={
                "owner_id": "user_agent",
                "statement_id": "stmt_agent_001",
                "init_cash": 500000,
            },
        )
        self.assertEqual(create_response.status_code, 200)
        payload = create_response.json()
        self.assertTrue(payload["agent_id"].startswith("agt_"))
        self.assertEqual(payload["statement_id"], "stmt_agent_001")
        self.assertEqual(payload["status"], "active")
        self.assertTrue((self.agent_registry_root / f"{payload['agent_id']}.json").exists())

        snapshot_response = self.client.get(f"/api/v1/agents/{payload['agent_id']}/snapshot")
        self.assertEqual(snapshot_response.status_code, 200)
        snapshot = snapshot_response.json()
        self.assertEqual(snapshot["agent_id"], payload["agent_id"])
        self.assertEqual(snapshot["owner_id"], "user_agent")
        self.assertEqual(snapshot["cash"], 500000.0)

        detail_response = self.client.get(f"/api/v1/agents/{payload['agent_id']}")
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.json()["statement_id"], "stmt_agent_001")

    def test_agent_creation_requires_generated_profile(self) -> None:
        upload_response = self.client.post(
            "/api/v1/statements/upload",
            data={"owner_id": "user_missing_profile", "market": "CN_A", "statement_id": "stmt_missing_profile"},
            files={
                "file": (
                    "agent.csv",
                    "trade_date,symbol,side,quantity,price,fee,tax\n2026-03-14,600519.SH,buy,100,1700.5,5,0\n",
                    "text/csv",
                )
            },
        )
        self.assertEqual(upload_response.status_code, 200)
        self.assertEqual(self.client.post("/api/v1/statements/stmt_missing_profile/parse").status_code, 200)

        create_response = self.client.post(
            "/api/v1/agents",
            json={
                "owner_id": "user_missing_profile",
                "statement_id": "stmt_missing_profile",
                "init_cash": 200000,
            },
        )
        self.assertEqual(create_response.status_code, 404)
        self.assertEqual(create_response.json()["error_code"], "PROFILE_NOT_FOUND")

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

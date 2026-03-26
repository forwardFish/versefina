from __future__ import annotations

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


class StatementStyleAssetsApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.object_store_root = Path(self.tempdir.name) / "object_store"
        self.statement_meta_root = Path(self.tempdir.name) / "statement_meta"
        self.statement_parse_report_root = Path(self.tempdir.name) / "statement_parse_reports"
        self.trade_record_root = Path(self.tempdir.name) / "trade_records"
        self.statement_style_root = Path(self.tempdir.name) / "statement_style"
        self.agent_profile_root = Path(self.tempdir.name) / "agent_profiles"
        self.agent_registry_root = Path(self.tempdir.name) / "agents"
        self.market_world_root = Path(self.tempdir.name) / "market_world"
        self.original_env = {
            "OBJECT_STORE_ROOT": os.environ.get("OBJECT_STORE_ROOT"),
            "STATEMENT_META_ROOT": os.environ.get("STATEMENT_META_ROOT"),
            "STATEMENT_PARSE_REPORT_ROOT": os.environ.get("STATEMENT_PARSE_REPORT_ROOT"),
            "TRADE_RECORD_ROOT": os.environ.get("TRADE_RECORD_ROOT"),
            "STATEMENT_STYLE_ROOT": os.environ.get("STATEMENT_STYLE_ROOT"),
            "AGENT_PROFILE_ROOT": os.environ.get("AGENT_PROFILE_ROOT"),
            "AGENT_REGISTRY_ROOT": os.environ.get("AGENT_REGISTRY_ROOT"),
            "MARKET_WORLD_ROOT": os.environ.get("MARKET_WORLD_ROOT"),
            "PUBLIC_BASE_URL": os.environ.get("PUBLIC_BASE_URL"),
            "OBJECT_STORE_BUCKET": os.environ.get("OBJECT_STORE_BUCKET"),
        }
        os.environ["OBJECT_STORE_ROOT"] = str(self.object_store_root)
        os.environ["STATEMENT_META_ROOT"] = str(self.statement_meta_root)
        os.environ["STATEMENT_PARSE_REPORT_ROOT"] = str(self.statement_parse_report_root)
        os.environ["TRADE_RECORD_ROOT"] = str(self.trade_record_root)
        os.environ["STATEMENT_STYLE_ROOT"] = str(self.statement_style_root)
        os.environ["AGENT_PROFILE_ROOT"] = str(self.agent_profile_root)
        os.environ["AGENT_REGISTRY_ROOT"] = str(self.agent_registry_root)
        os.environ["MARKET_WORLD_ROOT"] = str(self.market_world_root)
        os.environ["PUBLIC_BASE_URL"] = "http://127.0.0.1:8000"
        os.environ["OBJECT_STORE_BUCKET"] = "test-artifacts"
        self.client = TestClient(create_app())

    def tearDown(self) -> None:
        self.client.close()
        for key, value in self.original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        self.tempdir.cleanup()

    def test_style_feature_extraction_returns_behavior_metrics(self) -> None:
        statement_id = self._ingest_statement(
            "stmt_style_rich",
            "trade_date,symbol,side,quantity,price,fee,tax\n"
            "2026-03-14,600519.SH,buy,100,100,1,0\n"
            "2026-03-15,600519.SH,buy,100,105,1,0\n"
            "2026-03-18,600519.SH,sell,100,110,1,0\n"
            "2026-03-20,600519.SH,sell,100,95,1,0\n"
            "2026-03-21,300750.SZ,buy,50,200,1,0\n"
            "2026-03-24,300750.SZ,sell,50,190,1,0\n",
        )

        response = self.client.post(f"/api/v1/statements/{statement_id}/style-features")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["statement_id"], statement_id)
        self.assertIn("holding_period", payload)
        self.assertIn("add_reduce_pattern", payload)
        self.assertIn("momentum_preference", payload)
        self.assertIn("drawdown_tolerance", payload)
        self.assertGreater(payload["feature_vector"]["avg_holding_days"], 0)
        self.assertFalse(payload["low_confidence"])

        query_response = self.client.get(f"/api/v1/statements/{statement_id}/style-features")
        self.assertEqual(query_response.status_code, 200)
        self.assertEqual(query_response.json()["statement_id"], statement_id)

    def test_style_feature_extraction_marks_partial_when_sample_is_small(self) -> None:
        statement_id = self._ingest_statement(
            "stmt_style_small",
            "trade_date,symbol,side,quantity,price,fee,tax\n"
            "2026-03-14,600519.SH,buy,100,100,1,0\n"
            "2026-03-15,600519.SH,sell,100,101,1,0\n",
        )

        response = self.client.post(f"/api/v1/statements/{statement_id}/style-features")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "partial")
        self.assertTrue(payload["low_confidence"])
        self.assertIn("sample_size_below_four", payload["confidence_notes"])

    def test_market_style_embedding_is_stable_and_queryable(self) -> None:
        statement_id = self._ingest_statement(
            "stmt_embedding",
            "trade_date,symbol,side,quantity,price,fee,tax\n"
            "2026-03-14,300750.SZ,buy,100,200,1,0\n"
            "2026-03-15,300750.SZ,buy,100,205,1,0\n"
            "2026-03-17,300750.SZ,sell,100,215,1,0\n"
            "2026-03-18,300750.SZ,sell,100,210,1,0\n"
            "2026-03-20,688111.SH,buy,50,90,1,0\n"
            "2026-03-21,688111.SH,sell,50,95,1,0\n",
        )

        first = self.client.post(f"/api/v1/statements/{statement_id}/style-embedding")
        second = self.client.post(f"/api/v1/statements/{statement_id}/style-embedding")
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.json(), second.json())
        self.assertIn("holding_period_distribution", first.json())

        query_response = self.client.get(f"/api/v1/statements/{statement_id}/style-embedding")
        self.assertEqual(query_response.status_code, 200)
        self.assertEqual(query_response.json(), first.json())

    def test_archetype_seed_and_activation_calibration_are_derived_from_embedding(self) -> None:
        statement_id = self._ingest_statement(
            "stmt_archetype",
            "trade_date,symbol,side,quantity,price,fee,tax\n"
            "2026-03-14,600519.SH,buy,100,100,1,0\n"
            "2026-03-15,600519.SH,buy,100,106,1,0\n"
            "2026-03-16,600519.SH,sell,100,112,1,0\n"
            "2026-03-18,600519.SH,sell,100,109,1,0\n"
            "2026-03-19,000625.SZ,buy,100,20,1,0\n"
            "2026-03-21,000625.SZ,sell,100,24,1,0\n",
        )

        seed_response = self.client.post(f"/api/v1/statements/{statement_id}/archetype-seed")
        self.assertEqual(seed_response.status_code, 200)
        seed_payload = seed_response.json()
        self.assertIn("archetype_name", seed_payload)
        self.assertIn("participant_family", seed_payload)
        self.assertGreaterEqual(len(seed_payload["reaction_rules"]), 1)

        calibration_response = self.client.post(f"/api/v1/statements/{statement_id}/activation-calibration")
        self.assertEqual(calibration_response.status_code, 200)
        calibration_payload = calibration_response.json()
        self.assertIn("rules", calibration_payload)
        self.assertGreaterEqual(len(calibration_payload["rules"]), 1)
        self.assertEqual(calibration_payload["rules"][0]["event_type"], "supply_chain_price_shock")

        query_response = self.client.get(f"/api/v1/statements/{statement_id}/activation-calibration")
        self.assertEqual(query_response.status_code, 200)
        self.assertEqual(query_response.json()["statement_id"], statement_id)

    def _ingest_statement(self, statement_id: str, content: str) -> str:
        upload_response = self.client.post(
            "/api/v1/statements/upload",
            data={"owner_id": "style_user", "market": "CN_A", "statement_id": statement_id},
            files={"file": ("style.csv", content.encode("utf-8"), "text/csv")},
        )
        self.assertEqual(upload_response.status_code, 200)
        parse_response = self.client.post(f"/api/v1/statements/{statement_id}/parse")
        self.assertEqual(parse_response.status_code, 200)
        return statement_id


if __name__ == "__main__":
    unittest.main()

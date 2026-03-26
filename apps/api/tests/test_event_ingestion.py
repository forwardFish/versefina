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


class EventIngestionApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.original_env = {"EVENT_RUNTIME_ROOT": os.environ.get("EVENT_RUNTIME_ROOT")}
        os.environ["EVENT_RUNTIME_ROOT"] = str(Path(self.tempdir.name) / "events")
        self.client = TestClient(create_app())

    def tearDown(self) -> None:
        self.client.close()
        for key, value in self.original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        self.tempdir.cleanup()

    def test_create_event_returns_structure_and_mapping(self) -> None:
        response = self.client.post(
            "/api/v1/events",
            json={
                "title": "碳酸锂价格上涨",
                "body": "受停产和供给冲击影响，碳酸锂价格上涨，锂电材料链传导增强。",
                "source": "manual_text",
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["event_type"], "supply_chain_price_shock")
        self.assertEqual(payload["status"], "structured")
        self.assertIn("commodities", payload["structure"])
        self.assertIn("symbols", payload["mapping"])

    def test_non_whitelist_event_is_rejected(self) -> None:
        response = self.client.post(
            "/api/v1/events",
            json={
                "title": "政策鼓励消费",
                "body": "政策鼓励消费升级并扩大内需，但不属于当前事件白名单。",
                "source": "manual_text",
            },
        )
        self.assertEqual(response.status_code, 400)
        payload = response.json()
        self.assertEqual(payload["error_code"], "EVENT_NOT_IN_WHITELIST")


if __name__ == "__main__":
    unittest.main()

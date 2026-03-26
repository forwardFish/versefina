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


class EventStructuringApiTestCase(unittest.TestCase):
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

    def test_structure_event_returns_target_symbols_trigger_signals_and_confidence(self) -> None:
        create_response = self.client.post(
            "/api/v1/events",
            json={
                "title": "Copper inventory squeeze",
                "body": "supply shock and inventory draw push copper prices higher across the chain",
                "source": "manual_text",
            },
        )
        self.assertEqual(create_response.status_code, 200)
        event_id = create_response.json()["event_id"]

        structure_response = self.client.post(f"/api/v1/events/{event_id}/structure")
        self.assertEqual(structure_response.status_code, 200)
        payload = structure_response.json()
        self.assertEqual(payload["status"], "structured")
        self.assertEqual(payload["structure"]["event_type"], "supply_chain_price_shock")
        self.assertTrue(payload["structure"]["target_symbols"])
        self.assertTrue(payload["structure"]["trigger_signals"])
        self.assertGreater(payload["structure"]["confidence"], 0.0)

        query_response = self.client.get(f"/api/v1/events/{event_id}")
        self.assertEqual(query_response.status_code, 200)
        query_payload = query_response.json()
        self.assertEqual(query_payload["structure"]["target_symbols"], payload["structure"]["target_symbols"])
        self.assertEqual(query_payload["structure"]["trigger_signals"], payload["structure"]["trigger_signals"])
        self.assertEqual(query_payload["structure"]["confidence"], payload["structure"]["confidence"])

    def test_structure_missing_event_returns_not_found(self) -> None:
        response = self.client.post("/api/v1/events/missing-event/structure")
        self.assertEqual(response.status_code, 404)
        payload = response.json()
        self.assertEqual(payload["error_code"], "EVENT_NOT_FOUND")


if __name__ == "__main__":
    unittest.main()

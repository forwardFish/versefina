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


class ReportingApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.original_env = {
            "EVENT_RUNTIME_ROOT": os.environ.get("EVENT_RUNTIME_ROOT"),
            "SIMULATION_RUNTIME_ROOT": os.environ.get("SIMULATION_RUNTIME_ROOT"),
        }
        self.runtime_root = Path(self.tempdir.name) / "events"
        self.simulation_root = Path(self.tempdir.name) / "event_simulations"
        os.environ["EVENT_RUNTIME_ROOT"] = str(self.runtime_root)
        os.environ["SIMULATION_RUNTIME_ROOT"] = str(self.simulation_root)
        self.client = TestClient(create_app())

    def tearDown(self) -> None:
        self.client.close()
        for key, value in self.original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        self.tempdir.cleanup()

    def test_report_card_and_review_report_return_runtime_summaries(self) -> None:
        create_response = self.client.post(
            "/api/v1/events",
            json={
                "title": "Lithium price shock",
                "body": "supply shock drives lithium prices higher across the battery chain",
                "source": "manual_text",
            },
        )
        self.assertEqual(create_response.status_code, 200)
        event_id = create_response.json()["event_id"]
        run_response = self.client.post(f"/api/v1/events/{event_id}/simulation/run")
        self.assertEqual(run_response.status_code, 200)

        card_response = self.client.get(f"/api/v1/events/{event_id}/report-card")
        self.assertEqual(card_response.status_code, 200)
        report_card = card_response.json()
        self.assertEqual(report_card["event_id"], event_id)
        self.assertIn("graph_summary", report_card)
        self.assertIn("simulation_summary", report_card)
        self.assertEqual(report_card["simulation_summary"]["status"], "completed")

        review_response = self.client.get(f"/api/v1/events/{event_id}/review-report")
        self.assertEqual(review_response.status_code, 200)
        review_report = review_response.json()
        self.assertEqual(review_report["status"], "ready")
        self.assertEqual(review_report["timeline"]["status"], "complete")
        self.assertGreaterEqual(len(review_report["key_reasons"]), 1)

    def test_review_report_degrades_when_simulation_is_missing(self) -> None:
        create_response = self.client.post(
            "/api/v1/events",
            json={
                "title": "Copper price shock",
                "body": "supply shock lifts copper prices across mining and smelting names",
                "source": "manual_text",
            },
        )
        self.assertEqual(create_response.status_code, 200)
        event_id = create_response.json()["event_id"]

        response = self.client.get(f"/api/v1/events/{event_id}/review-report")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "degraded")
        self.assertEqual(payload["timeline"]["status"], "simulation_missing")


if __name__ == "__main__":
    unittest.main()

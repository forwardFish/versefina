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


class OutcomeReviewApiTestCase(unittest.TestCase):
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

    def test_record_outcome_persists_backfill_and_enriches_review_report(self) -> None:
        event_id = self._create_event("Lithium price shock")
        run_response = self.client.post(f"/api/v1/events/{event_id}/simulation/run")
        self.assertEqual(run_response.status_code, 200)

        outcome_response = self.client.post(
            f"/api/v1/events/{event_id}/outcomes",
            json={
                "horizon": "t1",
                "sector_performance": "outperform",
                "leader_performance": "outperform",
                "expansion_status": "confirmed",
                "sentiment_status": "supportive",
                "supporting_evidence": ["breadth:leaders_confirmed"],
            },
        )
        self.assertEqual(outcome_response.status_code, 200)
        outcome_payload = outcome_response.json()
        self.assertEqual(outcome_payload["event_id"], event_id)
        self.assertEqual(outcome_payload["dominant_scenario_actual"], "bull")
        self.assertIn(outcome_payload["score_label"], {"hit", "partial_hit"})
        self.assertTrue((self.runtime_root / "outcomes" / f"{event_id}-t1.json").exists())

        review_response = self.client.get(f"/api/v1/events/{event_id}/review-report")
        self.assertEqual(review_response.status_code, 200)
        review_payload = review_response.json()
        self.assertEqual(review_payload["outcome"]["dominant_scenario_actual"], "bull")
        self.assertEqual(review_payload["outcome"]["score_label"], outcome_payload["score_label"])

        outcomes_response = self.client.get(f"/api/v1/events/{event_id}/outcomes")
        self.assertEqual(outcomes_response.status_code, 200)
        outcomes_payload = outcomes_response.json()
        self.assertEqual(outcomes_payload["latest_outcome"]["horizon"], "t1")
        self.assertEqual(len(outcomes_payload["outcomes"]), 1)

    def test_record_outcome_rejects_missing_event(self) -> None:
        response = self.client.post(
            "/api/v1/events/missing-event/outcomes",
            json={
                "horizon": "t1",
                "sector_performance": "outperform",
                "leader_performance": "outperform",
                "expansion_status": "confirmed",
                "sentiment_status": "supportive",
            },
        )
        self.assertEqual(response.status_code, 404)
        payload = response.json()
        self.assertEqual(payload["error_code"], "EVENT_NOT_FOUND")

    def test_reliability_summary_marks_low_sample_size_until_multiple_events_exist(self) -> None:
        first_event_id = self._create_event("Copper price shock")
        self.client.post(f"/api/v1/events/{first_event_id}/simulation/run")
        self.client.post(
            f"/api/v1/events/{first_event_id}/outcomes",
            json={
                "horizon": "t1",
                "sector_performance": "outperform",
                "leader_performance": "outperform",
                "expansion_status": "confirmed",
                "sentiment_status": "supportive",
            },
        )
        low_sample_response = self.client.get(f"/api/v1/events/{first_event_id}/reliability")
        self.assertEqual(low_sample_response.status_code, 200)
        low_sample_payload = low_sample_response.json()
        self.assertEqual(low_sample_payload["status"], "low_sample_size")
        self.assertTrue(low_sample_payload["participants"][0]["low_sample_size"])

        second_event_id = self._create_event("Nickel price shock")
        self.client.post(f"/api/v1/events/{second_event_id}/simulation/run")
        self.client.post(
            f"/api/v1/events/{second_event_id}/outcomes",
            json={
                "horizon": "t3",
                "sector_performance": "outperform",
                "leader_performance": "underperform",
                "expansion_status": "partial",
                "sentiment_status": "supportive",
            },
        )
        ready_response = self.client.get(f"/api/v1/events/{second_event_id}/reliability")
        self.assertEqual(ready_response.status_code, 200)
        ready_payload = ready_response.json()
        self.assertEqual(ready_payload["status"], "ready")
        self.assertGreaterEqual(ready_payload["participants"][0]["sample_size"], 2)

    def test_why_endpoint_returns_structured_evidence_and_insufficient_evidence_when_missing(self) -> None:
        event_id = self._create_event("Tin price shock")

        insufficient_response = self.client.get(f"/api/v1/events/{event_id}/why")
        self.assertEqual(insufficient_response.status_code, 200)
        insufficient_payload = insufficient_response.json()
        self.assertEqual(insufficient_payload["status"], "insufficient_evidence")
        self.assertIn("simulation_missing", insufficient_payload["gaps"])

        self.client.post(f"/api/v1/events/{event_id}/simulation/run")
        self.client.post(
            f"/api/v1/events/{event_id}/outcomes",
            json={
                "horizon": "t3",
                "sector_performance": "underperform",
                "leader_performance": "underperform",
                "expansion_status": "failed",
                "sentiment_status": "negative",
                "analyst_note": "Follow-through faded after the initial breakout.",
            },
        )
        ready_response = self.client.get(f"/api/v1/events/{event_id}/why")
        self.assertEqual(ready_response.status_code, 200)
        ready_payload = ready_response.json()
        self.assertEqual(ready_payload["status"], "ready")
        self.assertIn("beliefs", ready_payload["evidence"])
        self.assertIn("simulation", ready_payload["evidence"])
        self.assertIn("outcome", ready_payload["evidence"])
        self.assertTrue(ready_payload["answer"])
        self.assertIn(ready_payload["actual_outcome"], ready_payload["answer"])

    def _create_event(self, title: str) -> str:
        response = self.client.post(
            "/api/v1/events",
            json={
                "title": title,
                "body": "supply shock drives prices higher across the battery chain and related miners",
                "source": "manual_text",
            },
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["event_id"]


if __name__ == "__main__":
    unittest.main()

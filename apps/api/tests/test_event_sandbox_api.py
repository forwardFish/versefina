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


class EventSandboxApiTestCase(unittest.TestCase):
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

    def test_event_sandbox_endpoints_cover_simulation_replay_and_validation(self) -> None:
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

        structure_response = self.client.post(f"/api/v1/events/{event_id}/structure")
        self.assertEqual(structure_response.status_code, 200)
        structure_payload = structure_response.json()
        self.assertEqual(structure_payload["status"], "structured")
        self.assertEqual(structure_payload["event_id"], event_id)

        prepare_response = self.client.post(f"/api/v1/events/{event_id}/participants/prepare")
        self.assertEqual(prepare_response.status_code, 200)
        prepare_payload = prepare_response.json()
        self.assertEqual(prepare_payload["status"], "prepared")
        self.assertTrue(prepare_payload["participant_roster"]["participants"])

        participants_response = self.client.get(f"/api/v1/events/{event_id}/participants")
        self.assertEqual(participants_response.status_code, 200)
        participants_payload = participants_response.json()
        self.assertEqual(participants_payload["status"], "prepared")
        self.assertEqual(len(participants_payload["participants"]), 20)

        simulate_response = self.client.post(f"/api/v1/events/{event_id}/simulate")
        self.assertEqual(simulate_response.status_code, 200)
        simulate_payload = simulate_response.json()
        self.assertEqual(simulate_payload["status"], "completed")
        self.assertGreaterEqual(len(simulate_payload["round_results"]), 3)

        summary_response = self.client.get(f"/api/v1/events/{event_id}/simulation")
        self.assertEqual(summary_response.status_code, 200)
        summary_payload = summary_response.json()
        self.assertEqual(summary_payload["status"], "ready")
        self.assertGreaterEqual(summary_payload["round_count"], 3)
        self.assertTrue(summary_payload["rounds"])

        rounds_response = self.client.get(f"/api/v1/events/{event_id}/simulation/rounds")
        self.assertEqual(rounds_response.status_code, 200)
        rounds_payload = rounds_response.json()
        self.assertEqual(rounds_payload["status"], "ready")
        first_round = rounds_payload["rounds"][0]
        self.assertTrue(first_round["participant_actions"])
        self.assertIn("execution_window", first_round)
        self.assertIn("market_state", first_round)
        self.assertIn("belief_snapshot", first_round)
        self.assertIn("scenario_snapshot", first_round)

        round_detail_response = self.client.get(
            f"/api/v1/events/{event_id}/simulation/rounds/{first_round['round_id']}"
        )
        self.assertEqual(round_detail_response.status_code, 200)
        round_detail_payload = round_detail_response.json()
        self.assertEqual(round_detail_payload["round_id"], first_round["round_id"])

        influence_response = self.client.get(f"/api/v1/events/{event_id}/influence-graph")
        self.assertEqual(influence_response.status_code, 200)
        influence_payload = influence_response.json()
        self.assertEqual(influence_payload["status"], "ready")
        self.assertTrue(influence_payload["rounds"])
        self.assertIn("edges", influence_payload["rounds"][0])
        if influence_payload["rounds"][0]["edges"]:
            self.assertIn("effect_on", influence_payload["rounds"][0]["edges"][0])

        influence_round_response = self.client.get(
            f"/api/v1/events/{event_id}/influence-graph/{first_round['round_id']}"
        )
        self.assertEqual(influence_round_response.status_code, 200)
        self.assertEqual(influence_round_response.json()["round_id"], first_round["round_id"])

        belief_response = self.client.get(f"/api/v1/events/{event_id}/belief")
        self.assertEqual(belief_response.status_code, 200)
        belief_payload = belief_response.json()
        self.assertEqual(belief_payload["status"], "ready")
        self.assertTrue(belief_payload["rounds"])

        scenarios_response = self.client.get(f"/api/v1/events/{event_id}/scenarios")
        self.assertEqual(scenarios_response.status_code, 200)
        scenarios_payload = scenarios_response.json()
        self.assertEqual(scenarios_payload["status"], "ready")
        self.assertTrue(scenarios_payload["rounds"])

        replay_response = self.client.get(f"/api/v1/events/{event_id}/replay")
        self.assertEqual(replay_response.status_code, 200)
        replay_payload = replay_response.json()
        self.assertEqual(replay_payload["status"], "ready")
        self.assertEqual(len(replay_payload["rounds"]), 5)

        report_response = self.client.get(f"/api/v1/events/{event_id}/report")
        self.assertEqual(report_response.status_code, 200)
        report_payload = report_response.json()
        self.assertEqual(report_payload["status"], "ready")
        self.assertIn("report_card", report_payload)
        self.assertIn("review_report", report_payload)

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

        validation_response = self.client.get(f"/api/v1/events/{event_id}/validation")
        self.assertEqual(validation_response.status_code, 200)
        validation_payload = validation_response.json()
        self.assertEqual(validation_payload["status"], "ready")
        self.assertEqual(validation_payload["report"]["status"], "ready")
        self.assertEqual(validation_payload["outcomes"]["status"], "ready")
        self.assertIn("participants", validation_payload["reliability"])

    def test_missing_event_returns_not_found_payloads(self) -> None:
        structure_response = self.client.post("/api/v1/events/missing-event/structure")
        self.assertEqual(structure_response.status_code, 404)
        self.assertEqual(structure_response.json()["error_code"], "EVENT_NOT_FOUND")

        participants_response = self.client.get("/api/v1/events/missing-event/participants")
        self.assertEqual(participants_response.status_code, 200)
        self.assertEqual(participants_response.json()["status"], "not_found")

        simulation_response = self.client.get("/api/v1/events/missing-event/simulation")
        self.assertEqual(simulation_response.status_code, 200)
        self.assertEqual(simulation_response.json()["status"], "simulation_missing")

        replay_response = self.client.get("/api/v1/events/missing-event/replay")
        self.assertEqual(replay_response.status_code, 200)
        self.assertEqual(replay_response.json()["status"], "simulation_missing")


if __name__ == "__main__":
    unittest.main()

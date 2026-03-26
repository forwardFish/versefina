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
from schemas.scenario_engine import ScenarioEngineResult


class EventSimulationApiTestCase(unittest.TestCase):
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

    def test_prepare_simulation_returns_runner_payload_and_persists_run(self) -> None:
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

        response = self.client.post(f"/api/v1/events/{event_id}/simulation/prepare")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "prepared")
        self.assertEqual(payload["simulation_run"]["status"], "prepared")
        self.assertGreaterEqual(len(payload["simulation_run"]["participant_states"]), 1)
        self.assertGreaterEqual(len(payload["simulation_run"]["rounds"]), 3)
        self.assertEqual(payload["runner_payload"]["run_id"], payload["simulation_run"]["run_id"])
        run_path = self.simulation_root / "runs" / f"{payload['simulation_run']['run_id']}.json"
        self.assertTrue(run_path.exists())
        persisted = json.loads(run_path.read_text(encoding="utf-8"))
        self.assertEqual(persisted["event_id"], event_id)

    def test_prepare_simulation_rejects_when_dominant_scenario_is_missing(self) -> None:
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
        container = self.client.app.state.container
        original_build_scenarios = container.scenario_engine.build_scenarios
        container.scenario_engine.build_scenarios = lambda incoming_event_id: ScenarioEngineResult(
            event_id=incoming_event_id,
            dominant_scenario="",
            graph_status="built",
            graph_metrics={},
            scenarios=[],
        )
        try:
            response = self.client.post(f"/api/v1/events/{event_id}/simulation/prepare")
        finally:
            container.scenario_engine.build_scenarios = original_build_scenarios
        self.assertEqual(response.status_code, 409)
        payload = response.json()
        self.assertEqual(payload["error_code"], "DOMINANT_SCENARIO_MISSING")

    def test_run_simulation_executes_three_to_five_rounds_and_persists_completion(self) -> None:
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

        response = self.client.post(f"/api/v1/events/{event_id}/simulation/run")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "completed")
        self.assertEqual(payload["simulation_run"]["status"], "completed")
        self.assertGreaterEqual(len(payload["round_results"]), 3)
        self.assertLessEqual(len(payload["round_results"]), 5)
        self.assertEqual(len(payload["round_results"]), payload["simulation_run"]["round_count"])
        self.assertGreaterEqual(len(payload["final_participant_states"]), 1)
        self.assertTrue(all(item["reason_codes"] for item in payload["round_results"]))
        self.assertTrue(any(state["state"] != "ready" for state in payload["final_participant_states"]))
        self.assertEqual(payload["timeline"]["status"], "complete")
        self.assertGreaterEqual(len(payload["timeline"]["first_move"]), 1)
        action_log_path = Path(payload["simulation_run"]["action_log_path"])
        self.assertTrue(action_log_path.exists())
        snapshot_paths = [Path(item) for item in payload["simulation_run"]["state_snapshots"]]
        self.assertGreaterEqual(len(snapshot_paths), 3)
        self.assertTrue(all(path.exists() for path in snapshot_paths))
        run_path = self.simulation_root / "runs" / f"{payload['simulation_run']['run_id']}.json"
        persisted = json.loads(run_path.read_text(encoding="utf-8"))
        self.assertEqual(persisted["status"], "completed")
        self.assertEqual(len(persisted["round_results"]), payload["simulation_run"]["round_count"])

        action_log_response = self.client.get(f"/api/v1/events/{event_id}/simulation/action-log")
        self.assertEqual(action_log_response.status_code, 200)
        action_log_payload = action_log_response.json()
        self.assertEqual(action_log_payload["status"], "ready")
        self.assertEqual(action_log_payload["run_id"], payload["simulation_run"]["run_id"])
        self.assertGreaterEqual(len(action_log_payload["entries"]), len(payload["round_results"]))
        self.assertTrue(all("actor_id" in item for item in action_log_payload["entries"]))

        snapshot_response = self.client.get(f"/api/v1/events/{event_id}/simulation/state-snapshots")
        self.assertEqual(snapshot_response.status_code, 200)
        snapshot_payload = snapshot_response.json()
        self.assertEqual(snapshot_payload["status"], "ready")
        self.assertEqual(snapshot_payload["run_id"], payload["simulation_run"]["run_id"])
        self.assertEqual(len(snapshot_payload["snapshots"]), payload["simulation_run"]["round_count"])
        self.assertTrue(all(item["participant_states"] for item in snapshot_payload["snapshots"]))

    def test_run_simulation_rejects_when_event_is_missing(self) -> None:
        response = self.client.post("/api/v1/events/missing-event/simulation/run")
        self.assertEqual(response.status_code, 404)
        payload = response.json()
        self.assertEqual(payload["error_code"], "EVENT_NOT_FOUND")

    def test_simulation_ledger_reports_missing_before_run_exists(self) -> None:
        action_log_response = self.client.get("/api/v1/events/missing-event/simulation/action-log")
        self.assertEqual(action_log_response.status_code, 200)
        self.assertEqual(action_log_response.json()["status"], "simulation_missing")

        snapshot_response = self.client.get("/api/v1/events/missing-event/simulation/state-snapshots")
        self.assertEqual(snapshot_response.status_code, 200)
        self.assertEqual(snapshot_response.json()["status"], "simulation_missing")


if __name__ == "__main__":
    unittest.main()

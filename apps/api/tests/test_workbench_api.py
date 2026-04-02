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


class WorkbenchApiTestCase(unittest.TestCase):
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

    def _prepare_event(self) -> str:
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
        self.client.post(f"/api/v1/events/{event_id}/structure")
        self.client.post(f"/api/v1/events/{event_id}/participants/prepare")
        self.client.post(f"/api/v1/events/{event_id}/simulate")
        return event_id

    def test_workbench_endpoints_cover_graph_stage_trade_pulse_and_ask(self) -> None:
        event_id = self._prepare_event()

        graph_response = self.client.get(f"/api/v1/events/{event_id}/graph-stage")
        self.assertEqual(graph_response.status_code, 200)
        graph_payload = graph_response.json()
        self.assertEqual(graph_payload["status"], "ready")
        self.assertTrue(graph_payload["nodes"])
        self.assertTrue(graph_payload["edges"])
        self.assertIn("shell", graph_payload)
        self.assertIn("current_highlights", graph_payload)
        self.assertIn("active_round_id", graph_payload["current_highlights"])
        self.assertIn("day_index", graph_payload["shell"])
        self.assertIn("trade_date", graph_payload["shell"])
        self.assertIn("is_incremental_generated", graph_payload["shell"])
        self.assertIn("actions_count", graph_payload["current_highlights"])

        clones_response = self.client.get(f"/api/v1/events/{event_id}/clones")
        self.assertEqual(clones_response.status_code, 200)
        clones_payload = clones_response.json()
        self.assertEqual(clones_payload["status"], "prepared")
        self.assertTrue(clones_payload["clones"])
        self.assertEqual(len(clones_payload["clones"]), 20)
        self.assertIn("capital_bucket", clones_payload["clones"][0])
        clone_id = clones_payload["clones"][0]["clone_id"]

        trade_pulse_response = self.client.get(f"/api/v1/events/{event_id}/trade-pulse")
        self.assertEqual(trade_pulse_response.status_code, 200)
        trade_pulse_payload = trade_pulse_response.json()
        self.assertEqual(trade_pulse_payload["status"], "ready")
        self.assertIn("trade_cards", trade_pulse_payload)
        self.assertIn("market_pulse_summary", trade_pulse_payload)
        self.assertIn("highlighted_clone_ids", trade_pulse_payload)
        self.assertIn("order_value", trade_pulse_payload["trade_cards"][0])
        self.assertIn("day_index", trade_pulse_payload)
        self.assertIn("trade_date", trade_pulse_payload)
        self.assertIn("is_incremental_generated", trade_pulse_payload)

        decision_trace_response = self.client.get(
            f"/api/v1/events/{event_id}/clones/{clone_id}/decision-trace"
        )
        self.assertEqual(decision_trace_response.status_code, 200)
        decision_trace_payload = decision_trace_response.json()
        self.assertEqual(decision_trace_payload["status"], "ready")
        self.assertEqual(decision_trace_payload["clone_id"], clone_id)
        self.assertIn("decision_chain", decision_trace_payload)
        self.assertIn("threshold_summary", decision_trace_payload)
        self.assertIn("day_index", decision_trace_payload)
        self.assertIn("trade_date", decision_trace_payload)
        self.assertIn("is_incremental_generated", decision_trace_payload)

        rounds_response = self.client.get(f"/api/v1/events/{event_id}/simulation/rounds")
        self.assertEqual(rounds_response.status_code, 200)
        rounds_payload = rounds_response.json()
        current_round_id = rounds_payload["rounds"][-1]["round_id"]
        transition_response = self.client.get(
            f"/api/v1/events/{event_id}/market-state/transitions/{current_round_id}"
        )
        self.assertEqual(transition_response.status_code, 200)
        transition_payload = transition_response.json()
        self.assertEqual(transition_payload["status"], "ready")
        self.assertIn("from_state", transition_payload)
        self.assertIn("market_metrics", transition_payload)

        report_response = self.client.get(f"/api/v1/events/{event_id}/workbench/report")
        self.assertEqual(report_response.status_code, 200)
        report_payload = report_response.json()
        self.assertEqual(report_payload["status"], "ready")
        self.assertIn("scoreboards", report_payload)

        ask_response = self.client.post(
            f"/api/v1/events/{event_id}/workbench/ask",
            json={"question": "谁在推动图谱", "ask_type": "graph"},
        )
        self.assertEqual(ask_response.status_code, 200)
        ask_payload = ask_response.json()
        self.assertEqual(ask_payload["status"], "ready")
        self.assertTrue(ask_payload["evidence_refs"])

        counterfactual_response = self.client.post(
            f"/api/v1/events/{event_id}/counterfactual",
            json={"question": "如果关键影响边减弱会怎样"},
        )
        self.assertEqual(counterfactual_response.status_code, 200)
        self.assertEqual(counterfactual_response.json()["ask_type"], "counterfactual")

    def test_workbench_missing_event_returns_structured_payloads(self) -> None:
        graph_response = self.client.get("/api/v1/events/missing-event/graph-stage")
        self.assertEqual(graph_response.status_code, 200)
        self.assertEqual(graph_response.json()["status"], "not_found")

        trade_pulse_response = self.client.get("/api/v1/events/missing-event/trade-pulse")
        self.assertEqual(trade_pulse_response.status_code, 200)
        self.assertIn(trade_pulse_response.json()["status"], {"simulation_missing", "not_found"})

        decision_trace_response = self.client.get(
            "/api/v1/events/missing-event/clones/missing-clone/decision-trace"
        )
        self.assertEqual(decision_trace_response.status_code, 200)
        self.assertEqual(decision_trace_response.json()["status"], "not_found")


if __name__ == "__main__":
    unittest.main()

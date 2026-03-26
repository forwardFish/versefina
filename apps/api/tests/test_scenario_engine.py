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


class ScenarioEngineApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.original_env = {"EVENT_RUNTIME_ROOT": os.environ.get("EVENT_RUNTIME_ROOT")}
        self.runtime_root = Path(self.tempdir.name) / "events"
        os.environ["EVENT_RUNTIME_ROOT"] = str(self.runtime_root)
        self.client = TestClient(create_app())

    def tearDown(self) -> None:
        self.client.close()
        for key, value in self.original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        self.tempdir.cleanup()

    def test_build_three_case_scenarios_from_graph_metrics(self) -> None:
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

        response = self.client.post(f"/api/v1/events/{event_id}/scenarios")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn(payload["dominant_scenario"], {"base", "bull", "bear"})
        self.assertEqual(len(payload["scenarios"]), 3)
        self.assertIn("supporter_count", payload["graph_metrics"])
        for scenario in payload["scenarios"]:
            self.assertIn("first_movers", scenario)
            self.assertIn("followers", scenario)
            self.assertIn("watchpoints", scenario)
            self.assertIn("invalidation_conditions", scenario)

    def test_build_three_case_scenarios_keeps_constrained_bull_bear_when_evidence_is_thin(self) -> None:
        casebook_root = self.runtime_root / "casebook"
        casebook_root.mkdir(parents=True, exist_ok=True)
        casebook_root.joinpath("evt-slim.json").write_text(
            json.dumps(
                {
                    "event_id": "evt-slim",
                    "record": {
                        "event_id": "evt-slim",
                        "title": "weak signal",
                        "body": "weak signal",
                        "source": "manual_text",
                        "event_time": "2026-03-25T00:00:00+00:00",
                        "status": "structured",
                    },
                    "structure": {
                        "event_id": "evt-slim",
                        "event_type": "supply_chain_price_shock",
                        "commodities": [],
                        "affected_symbols": [],
                        "monitor_signals": [],
                        "invalidation_conditions": [],
                        "summary": "evidence is still too thin",
                    },
                    "mapping": {"symbols": [], "sector": "", "commodity": ""},
                    "status": "structured",
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        response = self.client.post("/api/v1/events/evt-slim/scenarios")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["dominant_scenario"], "base")
        bull = next(item for item in payload["scenarios"] if item["scenario_id"] == "bull")
        bear = next(item for item in payload["scenarios"] if item["scenario_id"] == "bear")
        self.assertEqual(bull["first_movers"], [])
        self.assertEqual(bear["first_movers"], [])


if __name__ == "__main__":
    unittest.main()

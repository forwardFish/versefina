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


class EventCardsApiTestCase(unittest.TestCase):
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

    def test_event_card_returns_aggregated_read_model(self) -> None:
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

        response = self.client.get(f"/api/v1/events/{event_id}/card")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "ready")
        self.assertIn("graph_summary", payload)
        self.assertEqual(len(payload["scenarios"]), 3)
        self.assertGreaterEqual(len(payload["watchpoints"]), 1)

    def test_event_card_keeps_not_ready_status_when_scenarios_are_not_ready(self) -> None:
        casebook_root = self.runtime_root / "casebook"
        casebook_root.mkdir(parents=True, exist_ok=True)
        casebook_root.joinpath("evt-card-slim.json").write_text(
            json.dumps(
                {
                    "event_id": "evt-card-slim",
                    "record": {
                        "event_id": "evt-card-slim",
                        "title": "weak signal",
                        "body": "weak signal",
                        "source": "manual_text",
                        "event_time": "2026-03-25T00:00:00+00:00",
                        "status": "structured",
                    },
                    "structure": {
                        "event_id": "evt-card-slim",
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

        response = self.client.get("/api/v1/events/evt-card-slim/card")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "not_ready")


if __name__ == "__main__":
    unittest.main()

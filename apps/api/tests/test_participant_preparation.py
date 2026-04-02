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


class ParticipantPreparationApiTestCase(unittest.TestCase):
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

    def test_prepare_event_returns_participant_roster(self) -> None:
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

        prepare_response = self.client.post(f"/api/v1/events/{event_id}/prepare")
        self.assertEqual(prepare_response.status_code, 200)
        payload = prepare_response.json()
        self.assertEqual(payload["status"], "prepared")
        self.assertEqual(payload["participant_roster"]["status"], "prepared")
        participants = payload["participant_roster"]["participants"]
        self.assertEqual(len(participants), 20)
        first = participants[0]
        self.assertIn("participant_family", first)
        self.assertIn("authority_weight", first)
        self.assertIn("risk_budget_profile", first)
        self.assertIn("initial_state", first)
        self.assertIn("allowed_actions", first)
        self.assertIn("capital_bucket", first)
        self.assertIn("cash_available", first)
        self.assertIn("current_positions", first)
        self.assertIn("clone_index", first)
        self.assertTrue(first["allowed_actions"])
        self.assertIn(first["initial_state"], {"ready", "watching", "validated"})
        self.assertTrue(set(first["allowed_actions"]).issubset({
            "IGNORE",
            "WATCH",
            "VALIDATE",
            "INIT_BUY",
            "ADD_BUY",
            "REDUCE",
            "EXIT",
            "BROADCAST_BULL",
            "BROADCAST_BEAR",
        }))

    def test_prepare_event_degrades_when_evidence_is_incomplete(self) -> None:
        casebook_root = self.runtime_root / "casebook"
        casebook_root.mkdir(parents=True, exist_ok=True)
        casebook_root.joinpath("evt-insufficient.json").write_text(
            json.dumps(
                {
                    "event_id": "evt-insufficient",
                    "record": {
                        "event_id": "evt-insufficient",
                        "title": "weak signal",
                        "body": "weak signal",
                        "source": "manual_text",
                        "event_time": "2026-03-25T00:00:00+00:00",
                        "status": "structured",
                    },
                    "structure": {
                        "event_id": "evt-insufficient",
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

        response = self.client.post("/api/v1/events/evt-insufficient/prepare")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "degraded")
        self.assertEqual(payload["participant_roster"]["participants"], [])
        self.assertGreaterEqual(len(payload["participant_roster"]["blocked_reasons"]), 1)


if __name__ == "__main__":
    unittest.main()

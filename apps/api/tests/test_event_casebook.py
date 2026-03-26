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


class EventCasebookApiTestCase(unittest.TestCase):
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

    def test_prepare_event_promotes_casebook_and_supports_replay(self) -> None:
        create_response = self.client.post(
            "/api/v1/events",
            json={
                "title": "原油供给冲击",
                "body": "原油供给受限导致价格上涨，并向化工链传导。",
                "source": "manual_text",
            },
        )
        self.assertEqual(create_response.status_code, 200)
        event_id = create_response.json()["event_id"]

        prepare_response = self.client.post(f"/api/v1/events/{event_id}/prepare")
        self.assertEqual(prepare_response.status_code, 200)
        prepared = prepare_response.json()
        self.assertEqual(prepared["status"], "prepared")

        casebook_response = self.client.get(f"/api/v1/events/{event_id}/casebook")
        self.assertEqual(casebook_response.status_code, 200)
        casebook = casebook_response.json()
        self.assertEqual(casebook["status"], "prepared")
        self.assertEqual(casebook["event_id"], event_id)

    def test_missing_casebook_returns_not_found(self) -> None:
        response = self.client.get("/api/v1/events/evt-missing/casebook")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "not_found")


if __name__ == "__main__":
    unittest.main()

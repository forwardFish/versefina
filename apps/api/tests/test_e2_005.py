from __future__ import annotations

import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from app import create_app


class ParticipantRegistryDefaultsApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(create_app())

    def tearDown(self) -> None:
        self.client.close()

    def test_registry_snapshot_exposes_default_weights_and_budgets(self) -> None:
        response = self.client.post("/api/v1/participants/registry")
        self.assertEqual(response.status_code, 200)
        entries = response.json()["entries"]
        retail = next(item for item in entries if item["participant_family"] == "retail_fast_money")
        self.assertEqual(retail["authority_weight"], 0.62)
        self.assertEqual(retail["risk_budget_profile"], "high_turnover")
        self.assertEqual(retail["calibration_status"], "default")

    def test_unknown_registry_family_returns_not_found(self) -> None:
        response = self.client.post("/api/v1/participants/registry/unknown_family")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["status"], "not_found")


if __name__ == "__main__":
    unittest.main()

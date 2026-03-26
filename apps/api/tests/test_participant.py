from __future__ import annotations

import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from app import create_app


class ParticipantRegistryApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(create_app())

    def tearDown(self) -> None:
        self.client.close()

    def test_variants_endpoint_returns_fast_money_primary_variant(self) -> None:
        response = self.client.post("/api/v1/participants/variants")
        self.assertEqual(response.status_code, 200)
        variants = response.json()["variants"]
        retail_fast_money = next(item for item in variants if item["participant_family"] == "retail_fast_money")
        self.assertEqual(retail_fast_money["style_variant"], "fast_momentum")
        self.assertIn("authority_weight", retail_fast_money)
        self.assertIn("risk_budget_profile", retail_fast_money)

    def test_unknown_family_returns_not_found(self) -> None:
        response = self.client.post("/api/v1/participants/variants/unknown_family")
        self.assertEqual(response.status_code, 404)
        payload = response.json()
        self.assertEqual(payload["status"], "not_found")


if __name__ == "__main__":
    unittest.main()

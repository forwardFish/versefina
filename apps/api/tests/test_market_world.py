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


class MarketWorldApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.market_world_root = Path(self.tempdir.name) / "market_world"
        self.agent_registry_root = Path(self.tempdir.name) / "agents"
        self.original_env = {
            "MARKET_WORLD_ROOT": os.environ.get("MARKET_WORLD_ROOT"),
            "AGENT_REGISTRY_ROOT": os.environ.get("AGENT_REGISTRY_ROOT"),
        }
        os.environ["MARKET_WORLD_ROOT"] = str(self.market_world_root)
        os.environ["AGENT_REGISTRY_ROOT"] = str(self.agent_registry_root)
        self.client = TestClient(create_app())

    def tearDown(self) -> None:
        self.client.close()
        for key, value in self.original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        self.tempdir.cleanup()

    def test_trade_calendar_sync_persists_cache_and_serves_snapshot(self) -> None:
        sync_response = self.client.post(
            "/api/v1/admin/worlds/cn-a/calendar/sync",
            json={
                "start_date": "2026-03-13",
                "end_date": "2026-03-18",
                "market": "CN_A",
            },
        )
        self.assertEqual(sync_response.status_code, 200)
        payload = sync_response.json()
        self.assertEqual(payload["world_id"], "cn-a")
        self.assertEqual(payload["source"], "fallback_cn_calendar")
        self.assertIn("2026-03-16", payload["trading_days"])
        self.assertIn("2026-03-14", payload["closed_days"])
        self.assertTrue((self.market_world_root / "cn-a.calendar.json").exists())

        panorama_response = self.client.get("/api/v1/universe/panorama", params={"as_of_date": "2026-03-16"})
        self.assertEqual(panorama_response.status_code, 200)
        panorama = panorama_response.json()
        self.assertEqual(panorama["world_id"], "cn-a")
        self.assertEqual(panorama["trading_day"], "2026-03-16")
        self.assertEqual(panorama["next_trading_day"], "2026-03-17")
        self.assertEqual(panorama["market"], "CN_A")

        snapshot_response = self.client.get("/api/v1/worlds/cn-a/snapshot", params={"as_of_date": "2026-03-15"})
        self.assertEqual(snapshot_response.status_code, 200)
        snapshot = snapshot_response.json()
        self.assertEqual(snapshot["trading_day"], "2026-03-13")
        self.assertEqual(snapshot["next_trading_day"], "2026-03-16")
        self.assertEqual(snapshot["market_status"], "scheduled")


if __name__ == "__main__":
    unittest.main()

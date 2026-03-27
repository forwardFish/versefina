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


class FinahuntEventImportApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.original_env = {
            "EVENT_RUNTIME_ROOT": os.environ.get("EVENT_RUNTIME_ROOT"),
            "SIMULATION_RUNTIME_ROOT": os.environ.get("SIMULATION_RUNTIME_ROOT"),
            "FINAHUNT_RUNTIME_ROOT": os.environ.get("FINAHUNT_RUNTIME_ROOT"),
        }
        base_root = Path(self.tempdir.name)
        self.runtime_root = base_root / "events"
        self.simulation_root = base_root / "event_simulations"
        self.finahunt_root = base_root / "finahunt_runtime"
        os.environ["EVENT_RUNTIME_ROOT"] = str(self.runtime_root)
        os.environ["SIMULATION_RUNTIME_ROOT"] = str(self.simulation_root)
        os.environ["FINAHUNT_RUNTIME_ROOT"] = str(self.finahunt_root)
        self._write_finahunt_run()
        self.client = TestClient(create_app())

    def tearDown(self) -> None:
        self.client.close()
        for key, value in self.original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        self.tempdir.cleanup()

    def test_import_from_finahunt_creates_lineage_and_simulation(self) -> None:
        response = self.client.post(
            "/api/v1/events/from-finahunt",
            json={"auto_structure_prepare_simulate": True},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "ready")
        self.assertEqual(payload["lineage"]["status"], "ready")
        self.assertEqual(payload["lineage"]["finahunt_run_id"], "run-test123")
        event_id = payload["event_id"]

        lineage_response = self.client.get(f"/api/v1/events/{event_id}/lineage")
        self.assertEqual(lineage_response.status_code, 200)
        lineage_payload = lineage_response.json()
        self.assertEqual(lineage_payload["source_event_id"], "msg-001")
        self.assertEqual(lineage_payload["primary_theme"], "铜")

        event_response = self.client.get(f"/api/v1/events/{event_id}")
        self.assertEqual(event_response.status_code, 200)
        event_payload = event_response.json()
        self.assertEqual(event_payload["record"]["title"], "铜库存紧张引发供给冲击")

        simulation_response = self.client.get(f"/api/v1/events/{event_id}/simulation")
        self.assertEqual(simulation_response.status_code, 200)
        self.assertEqual(simulation_response.json()["status"], "ready")

    def _write_finahunt_run(self) -> None:
        run_root = self.finahunt_root / "run-test123"
        run_root.mkdir(parents=True, exist_ok=True)
        (run_root / "manifest.json").write_text(
            json.dumps(
                {
                    "run_id": "run-test123",
                    "trace_id": "trace-test123",
                    "created_at": "2026-03-27T10:00:00+00:00",
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        (run_root / "ranked_result_feed.json").write_text(
            json.dumps(
                [
                    {
                        "rank_position": 1,
                        "theme_name": "铜",
                        "relevance_score": 88.2,
                        "fermentation_phase": "propagating",
                        "top_evidence": [
                            {
                                "event_id": "msg-001",
                                "title": "铜库存紧张引发供给冲击",
                            }
                        ],
                    }
                ],
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        (run_root / "daily_message_workbench.json").write_text(
            json.dumps(
                {
                    "run_id": "run-test123",
                    "status": "ready",
                    "messages": [
                        {
                            "message": {
                                "message_id": "msg-001",
                                "title": "铜库存紧张引发供给冲击",
                                "summary": "海外仓库存下降推动铜价走高，产业链渠道开始强化涨价预期。",
                                "message_text": "海外仓库存下降推动铜价走高，产业链渠道开始强化涨价预期。",
                                "event_subject": "铜",
                                "event_time": "2026-03-27T09:00:00+00:00",
                                "source_name": "财联社",
                                "source_url": "https://example.com/copper",
                                "source_priority": "P1",
                                "related_themes": ["铜", "资源品"],
                                "related_industries": ["有色金属"],
                            },
                            "impact": {
                                "primary_theme": "铜",
                                "impact_direction": "正向扩散",
                            },
                        }
                    ],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )


if __name__ == "__main__":
    unittest.main()

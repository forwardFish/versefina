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


class RoadmapAcceptancePackApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.repo_root = Path(self.tempdir.name) / "repo"
        self.object_store_root = Path(self.tempdir.name) / "object_store"
        self.statement_meta_root = Path(self.tempdir.name) / "statement_meta"
        self.statement_parse_report_root = Path(self.tempdir.name) / "statement_parse_reports"
        self.trade_record_root = Path(self.tempdir.name) / "trade_records"
        self.statement_style_root = Path(self.tempdir.name) / "statement_style"
        self.agent_profile_root = Path(self.tempdir.name) / "agent_profiles"
        self.agent_registry_root = Path(self.tempdir.name) / "agents"
        self.market_world_root = Path(self.tempdir.name) / "market_world"
        self.roadmap_acceptance_root = Path(self.tempdir.name) / "roadmap_acceptance"
        self.original_env = {
            "OBJECT_STORE_ROOT": os.environ.get("OBJECT_STORE_ROOT"),
            "STATEMENT_META_ROOT": os.environ.get("STATEMENT_META_ROOT"),
            "STATEMENT_PARSE_REPORT_ROOT": os.environ.get("STATEMENT_PARSE_REPORT_ROOT"),
            "TRADE_RECORD_ROOT": os.environ.get("TRADE_RECORD_ROOT"),
            "STATEMENT_STYLE_ROOT": os.environ.get("STATEMENT_STYLE_ROOT"),
            "AGENT_PROFILE_ROOT": os.environ.get("AGENT_PROFILE_ROOT"),
            "AGENT_REGISTRY_ROOT": os.environ.get("AGENT_REGISTRY_ROOT"),
            "MARKET_WORLD_ROOT": os.environ.get("MARKET_WORLD_ROOT"),
            "ROADMAP_SOURCE_ROOT": os.environ.get("ROADMAP_SOURCE_ROOT"),
            "ROADMAP_ACCEPTANCE_ROOT": os.environ.get("ROADMAP_ACCEPTANCE_ROOT"),
            "PUBLIC_BASE_URL": os.environ.get("PUBLIC_BASE_URL"),
            "OBJECT_STORE_BUCKET": os.environ.get("OBJECT_STORE_BUCKET"),
        }
        os.environ["OBJECT_STORE_ROOT"] = str(self.object_store_root)
        os.environ["STATEMENT_META_ROOT"] = str(self.statement_meta_root)
        os.environ["STATEMENT_PARSE_REPORT_ROOT"] = str(self.statement_parse_report_root)
        os.environ["TRADE_RECORD_ROOT"] = str(self.trade_record_root)
        os.environ["STATEMENT_STYLE_ROOT"] = str(self.statement_style_root)
        os.environ["AGENT_PROFILE_ROOT"] = str(self.agent_profile_root)
        os.environ["AGENT_REGISTRY_ROOT"] = str(self.agent_registry_root)
        os.environ["MARKET_WORLD_ROOT"] = str(self.market_world_root)
        os.environ["ROADMAP_SOURCE_ROOT"] = str(self.repo_root)
        os.environ["ROADMAP_ACCEPTANCE_ROOT"] = str(self.roadmap_acceptance_root)
        os.environ["PUBLIC_BASE_URL"] = "http://127.0.0.1:8000"
        os.environ["OBJECT_STORE_BUCKET"] = "test-artifacts"
        self._write_repo_fixture()
        self.client = TestClient(create_app())

    def tearDown(self) -> None:
        self.client.close()
        for key, value in self.original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        self.tempdir.cleanup()

    def test_build_acceptance_pack_persists_boundary_and_migration_contract(self) -> None:
        response = self.client.post("/api/v1/roadmaps/1.6/acceptance-pack")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["roadmap_id"], "roadmap_1_6")
        self.assertEqual(payload["status"], "ready")
        self.assertEqual(payload["p0_boundaries"][0]["priority"], "P0")
        self.assertEqual(payload["p1_boundaries"][0]["priority"], "P1")
        self.assertEqual(payload["migration_map"][0]["legacy_sprint"], "Sprint 1")
        self.assertIn(str(self.repo_root / "NOW.md"), payload["continuity_files"])
        self.assertEqual(payload["current_handoff"]["story"], "E7-005")
        persisted = self.client.get("/api/v1/roadmaps/1.6/acceptance-pack")
        self.assertEqual(persisted.status_code, 200)
        self.assertEqual(persisted.json()["status"], "ready")

    def test_build_acceptance_pack_rejects_missing_support_file(self) -> None:
        overview_path = self.repo_root / "tasks" / "sprint_overview_1_6_event_participant_first.md"
        overview_path.unlink()

        response = self.client.post("/api/v1/roadmaps/1.6/acceptance-pack")
        self.assertEqual(response.status_code, 404)
        payload = response.json()
        self.assertEqual(payload["error_code"], "ROADMAP_SUPPORT_FILE_MISSING")

    def _write_repo_fixture(self) -> None:
        (self.repo_root / "docs" / "requirements").mkdir(parents=True, exist_ok=True)
        (self.repo_root / "docs" / "handoff").mkdir(parents=True, exist_ok=True)
        (self.repo_root / "tasks").mkdir(parents=True, exist_ok=True)
        (self.repo_root / "NOW.md").write_text("# NOW\n", encoding="utf-8")
        (self.repo_root / "STATE.md").write_text("# STATE\n", encoding="utf-8")
        (self.repo_root / "DECISIONS.md").write_text("# DECISIONS\n", encoding="utf-8")
        (self.repo_root / "tasks" / "sprint_overview_1_6_event_participant_first.md").write_text(
            "# Sprint Overview\nRoadmap 1.6 overview.\n",
            encoding="utf-8",
        )
        (self.repo_root / "docs" / "handoff" / "current_handoff.md").write_text(
            "# Current Handoff\n\n"
            "- Sprint: roadmap_1_6_sprint_7_mirror_agent_and_distribution_calibration\n"
            "- Story: E7-005\n"
            "- Status: interrupted\n\n"
            "## Next Action\nResume E7-005.\n\n"
            "## Recovery Command\npython cli.py run-roadmap --resume\n",
            encoding="utf-8",
        )
        for sprint in range(1, 8):
            path = self.repo_root / "docs" / "requirements" / f"e{sprint}_001_delivery.md"
            path.write_text(
                f"# E{sprint}-001 Delivery\n\n- Sprint {sprint} evidence is ready.\n",
                encoding="utf-8",
            )


if __name__ == "__main__":
    unittest.main()

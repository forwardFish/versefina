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


class DemoRuntimeShowcaseApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.runtime_root = Path(self.tempdir.name) / ".runtime"
        self.repo_root = Path(self.tempdir.name) / "repo"
        self.object_store_root = self.runtime_root / "object_store"
        self.statement_meta_root = self.runtime_root / "statement_meta"
        self.statement_parse_report_root = self.runtime_root / "statement_parse_reports"
        self.trade_record_root = self.runtime_root / "trade_records"
        self.statement_style_root = self.runtime_root / "statement_style"
        self.agent_profile_root = self.runtime_root / "agent_profiles"
        self.agent_registry_root = self.runtime_root / "agents"
        self.market_world_root = self.runtime_root / "market_world"
        self.event_runtime_root = self.runtime_root / "events"
        self.simulation_runtime_root = self.runtime_root / "event_simulations"
        self.roadmap_acceptance_root = self.runtime_root / "roadmap_acceptance"
        self.original_env = {key: os.environ.get(key) for key in self._env_keys()}
        self._set_env()

    def tearDown(self) -> None:
        for key, value in self.original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        self.tempdir.cleanup()

    def test_runtime_showcase_returns_full_real_sample(self) -> None:
        self._write_full_fixture()
        with TestClient(create_app()) as client:
            response = client.get("/api/v1/demo/runtime-showcase")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["event_demo"]["status"], "ready")
        self.assertEqual(payload["event_demo"]["event_id"], "evt-demo-001")
        self.assertEqual(payload["statement_demo"]["status"], "ready")
        self.assertEqual(payload["statement_demo"]["statement_id"], "stmt-001")
        self.assertEqual(payload["acceptance_demo"]["status"], "ready")
        self.assertEqual(payload["acceptance_demo"]["roadmap_id"], "roadmap_1_6")
        self.assertIn("evt-demo-001", payload["event_demo"]["why"]["answer"])

    def test_runtime_showcase_marks_missing_sections_without_throwing(self) -> None:
        self._write_event_only_fixture()
        with TestClient(create_app()) as client:
            response = client.get("/api/v1/demo/runtime-showcase")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["event_demo"]["status"], "ready")
        self.assertEqual(payload["statement_demo"]["status"], "missing")
        self.assertEqual(payload["acceptance_demo"]["status"], "missing")

    def test_runtime_showcase_returns_empty_state_for_blank_runtime(self) -> None:
        self._ensure_dirs()
        with TestClient(create_app()) as client:
            response = client.get("/api/v1/demo/runtime-showcase")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["event_demo"]["status"], "missing")
        self.assertEqual(payload["statement_demo"]["status"], "missing")
        self.assertEqual(payload["acceptance_demo"]["status"], "missing")

    def _set_env(self) -> None:
        os.environ["OBJECT_STORE_ROOT"] = str(self.object_store_root)
        os.environ["STATEMENT_META_ROOT"] = str(self.statement_meta_root)
        os.environ["STATEMENT_PARSE_REPORT_ROOT"] = str(self.statement_parse_report_root)
        os.environ["TRADE_RECORD_ROOT"] = str(self.trade_record_root)
        os.environ["STATEMENT_STYLE_ROOT"] = str(self.statement_style_root)
        os.environ["AGENT_PROFILE_ROOT"] = str(self.agent_profile_root)
        os.environ["AGENT_REGISTRY_ROOT"] = str(self.agent_registry_root)
        os.environ["MARKET_WORLD_ROOT"] = str(self.market_world_root)
        os.environ["EVENT_RUNTIME_ROOT"] = str(self.event_runtime_root)
        os.environ["SIMULATION_RUNTIME_ROOT"] = str(self.simulation_runtime_root)
        os.environ["ROADMAP_SOURCE_ROOT"] = str(self.repo_root)
        os.environ["ROADMAP_ACCEPTANCE_ROOT"] = str(self.roadmap_acceptance_root)
        os.environ["PUBLIC_BASE_URL"] = "http://127.0.0.1:8001"
        os.environ["OBJECT_STORE_BUCKET"] = "test-artifacts"

    def _env_keys(self) -> list[str]:
        return [
            "OBJECT_STORE_ROOT",
            "STATEMENT_META_ROOT",
            "STATEMENT_PARSE_REPORT_ROOT",
            "TRADE_RECORD_ROOT",
            "STATEMENT_STYLE_ROOT",
            "AGENT_PROFILE_ROOT",
            "AGENT_REGISTRY_ROOT",
            "MARKET_WORLD_ROOT",
            "EVENT_RUNTIME_ROOT",
            "SIMULATION_RUNTIME_ROOT",
            "ROADMAP_SOURCE_ROOT",
            "ROADMAP_ACCEPTANCE_ROOT",
            "PUBLIC_BASE_URL",
            "OBJECT_STORE_BUCKET",
        ]

    def _ensure_dirs(self) -> None:
        for path in [
            self.object_store_root,
            self.statement_meta_root,
            self.statement_parse_report_root,
            self.trade_record_root,
            self.statement_style_root / "features",
            self.statement_style_root / "mirror_agents",
            self.statement_style_root / "mirror_validation",
            self.statement_style_root / "distribution_calibration",
            self.agent_profile_root,
            self.agent_registry_root,
            self.market_world_root,
            self.event_runtime_root / "records",
            self.event_runtime_root / "structures",
            self.event_runtime_root / "mappings",
            self.event_runtime_root / "casebook",
            self.event_runtime_root / "outcomes",
            self.simulation_runtime_root / "runs",
            self.roadmap_acceptance_root,
        ]:
            path.mkdir(parents=True, exist_ok=True)
        (self.repo_root / "docs" / "handoff").mkdir(parents=True, exist_ok=True)
        (self.repo_root / "docs" / "handoff" / "current_handoff.md").write_text(
            "# Current Handoff\n\n- Status: completed\n",
            encoding="utf-8",
        )

    def _write_full_fixture(self) -> None:
        self._ensure_dirs()
        self._write_json(
            self.event_runtime_root / "records" / "evt-demo-001.json",
            {
                "event_id": "evt-demo-001",
                "title": "Copper squeeze",
                "body": "supply shock drives copper higher",
                "event_time": "2026-03-25T10:00:00+00:00",
            },
        )
        self._write_json(
            self.event_runtime_root / "structures" / "evt-demo-001.json",
            {
                "event_type": "supply_chain_price_shock",
                "impact_direction": "up",
                "affected_sector": "materials",
                "watchpoints": ["inventory_drawdown"],
                "invalidation_conditions": ["spot reverses"],
            },
        )
        self._write_json(
            self.event_runtime_root / "mappings" / "evt-demo-001.json",
            {
                "primary_theme": "battery_materials",
                "target_symbols": ["000001.SZ"],
                "theme_rationale": ["inventory tightness"],
            },
        )
        self._write_json(self.event_runtime_root / "casebook" / "evt-demo-001.json", {"watchpoints": ["inventory_drawdown"]})
        self._write_json(
            self.simulation_runtime_root / "runs" / "evt-demo-001-run-001.json",
            {
                "run_id": "evt-demo-001-run-001",
                "status": "completed",
                "dominant_scenario": "base",
                "round_count": 3,
                "participant_states": [
                    {
                        "participant_id": "institution_confirmation:trend_confirmation",
                        "participant_family": "institution_confirmation",
                        "role": "first_move",
                        "stance": "constructive",
                        "authority_weight": 0.78,
                        "state": "accelerating",
                    }
                ],
                "timeline": {
                    "status": "complete",
                    "turning_points": ["round-3"],
                    "first_move": [{"participant_id": "institution_confirmation:trend_confirmation"}],
                    "follow_on": [{"participant_id": "industry_research:follow_on"}],
                },
                "watchpoints": ["inventory_drawdown"],
                "action_log_path": "D:/tmp/actions.jsonl",
            },
        )
        self._write_json(
            self.event_runtime_root / "outcomes" / "evt-demo-001-t1.json",
            {
                "status": "ready",
                "horizon": "t1",
                "dominant_scenario_actual": "bull",
                "score_label": "partial_hit",
                "sector_performance": "outperform",
                "leader_performance": "outperform",
                "supporting_evidence": ["sector:outperform"],
            },
        )
        self._write_json(
            self.statement_meta_root / "stmt-001.json",
            {
                "statement_id": "stmt-001",
                "owner_id": "owner-1",
                "market": "CN_A",
                "file_name": "demo.xls",
                "upload_status": "parsed",
                "detected_file_type": "xls",
            },
        )
        self._write_json(
            self.statement_parse_report_root / "stmt-001.json",
            {"status": "ready", "parser_key": "statement_excel_parser", "trade_count": 60},
        )
        self._write_json(
            self.trade_record_root / "stmt-001.json",
            {"status": "ready", "trade_count": 2, "trades": [{"symbol": "000001.SZ"}, {"symbol": "300750.SZ"}]},
        )
        self._write_json(
            self.statement_style_root / "features" / "stmt-001.json",
            {"status": "ready", "trade_count": 60, "feature_vector": {"avg_holding_days": 2.42}},
        )
        self._write_json(
            self.statement_style_root / "mirror_agents" / "stmt-001.json",
            {
                "status": "ready",
                "archetype_name": "generic_balanced",
                "participant_family": "quant_risk_budget",
                "profile": {"style_tags": ["medium"]},
                "evidence": ["style_embedding"],
            },
        )
        self._write_json(
            self.statement_style_root / "mirror_validation" / "stmt-001.json",
            {"status": "ready", "grading": "B", "risk_posture": "guarded", "notes": ["stable enough"]},
        )
        self._write_json(
            self.statement_style_root / "distribution_calibration" / "stmt-001.json",
            {"status": "ready", "sample_size": 3, "hit_rate": 0.62, "segments": [{"label": "swing"}]},
        )
        self._write_json(
            self.roadmap_acceptance_root / "roadmap_1_6.json",
            {
                "roadmap_id": "roadmap_1_6",
                "status": "ready",
                "headline": "Acceptance pack ready",
                "p0_boundaries": [{"priority": "P0", "label": "Main lane"}],
                "p1_boundaries": [{"priority": "P1", "label": "Extension lane"}],
                "current_handoff": {"status": "completed", "story": "none"},
                "delivery_artifacts": [{"story_id": "E1-003", "summary": "event ingestion"}],
            },
        )

    def _write_event_only_fixture(self) -> None:
        self._ensure_dirs()
        self._write_json(
            self.event_runtime_root / "records" / "evt-demo-002.json",
            {
                "event_id": "evt-demo-002",
                "title": "Nickel squeeze",
                "body": "supply shock drives nickel higher",
                "event_time": "2026-03-25T10:00:00+00:00",
            },
        )

    def _write_json(self, path: Path, payload: dict[str, object]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import sys
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from app import create_app
from main import build_app_metadata


class ArchitectureScaffoldTestCase(unittest.TestCase):
    def test_app_metadata_reports_ok(self) -> None:
        metadata = build_app_metadata()
        self.assertEqual(metadata["service"], "versefina-api")
        self.assertEqual(metadata["status"], "ok")

    def test_app_exposes_required_routes(self) -> None:
        app = create_app()
        paths = {getattr(route, "path", "") for route in getattr(app, "routes", [])}
        expected = {
            "/health",
            "/api/v1/statements/upload",
            "/api/v1/statements/{statement_id}/parse",
            "/api/v1/statements/{statement_id}/status",
            "/api/v1/statements/{statement_id}",
            "/api/v1/statements/{statement_id}/parse-report",
            "/api/v1/agents/register",
            "/api/v1/actions/submit",
            "/api/v1/rankings",
            "/api/v1/universe/panorama",
            "/api/v1/adapter/openclaw/register",
        }
        self.assertTrue(expected.issubset(paths))

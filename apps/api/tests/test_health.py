from __future__ import annotations

import sys
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from main import build_app_metadata


class HealthCheckTestCase(unittest.TestCase):
    def test_build_app_metadata_returns_ok_status(self) -> None:
        metadata = build_app_metadata()
        self.assertEqual(metadata["service"], "versefina-api")
        self.assertEqual(metadata["status"], "ok")


if __name__ == "__main__":
    unittest.main()

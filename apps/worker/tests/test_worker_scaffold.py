from __future__ import annotations

import sys
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from main import build_worker_manifest


class WorkerScaffoldTestCase(unittest.TestCase):
    def test_worker_manifest(self) -> None:
        manifest = build_worker_manifest()
        self.assertEqual(manifest["service"], "versefina-worker")
        self.assertEqual(manifest["primary_job"], "daily-simulation-loop")
        self.assertEqual(manifest["mode"], "standalone")

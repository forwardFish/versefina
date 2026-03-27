from __future__ import annotations

import sys
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from schemas.demo import RuntimeShowcaseResponse as LegacyRuntimeShowcaseResponse
from schemas.demo_showcase import RuntimeShowcaseResponse


class DemoShowcaseSchemaTestCase(unittest.TestCase):
    def test_runtime_showcase_response_to_dict_keeps_nested_payloads(self) -> None:
        response = RuntimeShowcaseResponse(
            generated_at="2026-03-27T18:30:00+08:00",
            event_demo={"status": "ready", "event_id": "evt-demo-001"},
            statement_demo={"status": "ready", "statement_id": "stmt-001"},
            acceptance_demo={"status": "ready", "roadmap_id": "roadmap_1_7"},
            source_paths={"event_demo": {"record": "D:/tmp/evt-demo-001.json"}},
        )

        payload = response.to_dict()

        self.assertEqual(payload["generated_at"], "2026-03-27T18:30:00+08:00")
        self.assertEqual(payload["event_demo"]["event_id"], "evt-demo-001")
        self.assertEqual(payload["statement_demo"]["statement_id"], "stmt-001")
        self.assertEqual(payload["acceptance_demo"]["roadmap_id"], "roadmap_1_7")
        self.assertEqual(payload["source_paths"]["event_demo"]["record"], "D:/tmp/evt-demo-001.json")

    def test_legacy_demo_schema_import_points_to_same_runtime_showcase_response(self) -> None:
        self.assertIs(LegacyRuntimeShowcaseResponse, RuntimeShowcaseResponse)


if __name__ == "__main__":
    unittest.main()

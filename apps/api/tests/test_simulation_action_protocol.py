from __future__ import annotations

import sys
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from schemas.simulation import (  # noqa: E402
    SIMULATION_ACTION_PROTOCOL,
    SIMULATION_ACTION_PROTOCOL_DEFINITIONS,
    normalize_simulation_action_name,
)


class SimulationActionProtocolTestCase(unittest.TestCase):
    def test_action_protocol_contains_expected_p0_vocabulary(self) -> None:
        self.assertEqual(
            SIMULATION_ACTION_PROTOCOL,
            (
                "IGNORE",
                "WATCH",
                "VALIDATE",
                "INIT_BUY",
                "ADD_BUY",
                "REDUCE",
                "EXIT",
                "BROADCAST_BULL",
                "BROADCAST_BEAR",
            ),
        )
        self.assertEqual(len(SIMULATION_ACTION_PROTOCOL_DEFINITIONS), len(SIMULATION_ACTION_PROTOCOL))

    def test_normalize_action_name_rejects_unsupported_action(self) -> None:
        self.assertEqual(normalize_simulation_action_name("init_buy"), "INIT_BUY")
        with self.assertRaises(ValueError):
            normalize_simulation_action_name("panic_sell")


if __name__ == "__main__":
    unittest.main()

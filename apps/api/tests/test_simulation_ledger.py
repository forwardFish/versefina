from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from domain.simulation_ledger.service import SimulationLedgerService  # noqa: E402
from schemas.simulation import SimulationParticipantUpdate, SimulationRoundResult  # noqa: E402


class SimulationLedgerServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.runtime_root = Path(self.tempdir.name) / "event_simulations"
        self.ledger = SimulationLedgerService(self.runtime_root)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_persist_and_load_round_results(self) -> None:
        round_results = [
            SimulationRoundResult(
                round_id="round-1",
                order=1,
                focus="Ignition",
                objective="Start the path",
                status="completed",
                participant_updates=[
                    SimulationParticipantUpdate(
                        participant_id="retail_fast_money:fast_momentum",
                        action_type="init_buy",
                        previous_state="ready",
                        next_state="engaged",
                        round_id="round-1",
                        actor_id="retail_fast_money:fast_momentum",
                        target_id="LITHIUM",
                        action_name="INIT_BUY",
                        confidence=0.76,
                        reason_code="scenario:bull",
                        reason_codes=["scenario:bull", "action:init_buy"],
                        execution_window="pre_open",
                        target_symbol="LITHIUM",
                        order_side="buy",
                        order_value=150000.0,
                        order_value_range_min=120000.0,
                        order_value_range_max=170000.0,
                        position_before=0.0,
                        position_after=150000.0,
                        cash_before=500000.0,
                        cash_after=350000.0,
                    )
                ],
                participant_states=[
                    {
                        "participant_id": "retail_fast_money:fast_momentum",
                        "participant_family": "retail_fast_money",
                        "state": "engaged",
                    }
                ],
                reason_codes=["round:1"],
            )
        ]

        action_log_path, snapshot_paths = self.ledger.persist_round_results(
            event_id="evt-demo",
            run_id="evt-demo-run-001",
            round_results=round_results,
        )

        self.assertTrue(action_log_path.exists())
        self.assertEqual(len(snapshot_paths), 1)
        self.assertTrue(snapshot_paths[0].exists())

        (self.runtime_root / "runs").mkdir(parents=True, exist_ok=True)
        (self.runtime_root / "runs" / "evt-demo-run-001.json").write_text("{}", encoding="utf-8")

        action_log = self.ledger.load_action_log("evt-demo")
        self.assertEqual(action_log.status, "ready")
        self.assertEqual(len(action_log.entries), 1)
        self.assertEqual(action_log.entries[0].actor_id, "retail_fast_money:fast_momentum")
        self.assertEqual(action_log.entries[0].target_id, "LITHIUM")
        self.assertEqual(action_log.entries[0].target_symbol, "LITHIUM")
        self.assertEqual(action_log.entries[0].order_side, "buy")

        snapshots = self.ledger.load_state_snapshots("evt-demo")
        self.assertEqual(snapshots.status, "ready")
        self.assertEqual(len(snapshots.snapshots), 1)
        self.assertEqual(snapshots.snapshots[0].participant_states[0]["state"], "engaged")

    def test_missing_event_returns_simulation_missing(self) -> None:
        self.assertEqual(self.ledger.load_action_log("missing-event").status, "simulation_missing")
        self.assertEqual(self.ledger.load_state_snapshots("missing-event").status, "simulation_missing")


if __name__ == "__main__":
    unittest.main()

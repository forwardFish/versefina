from __future__ import annotations

import unittest

from domain.event_simulation.timeline import build_simulation_timeline
from schemas.simulation import SimulationParticipantUpdate, SimulationRoundResult


class SimulationTimelineTestCase(unittest.TestCase):
    def test_timeline_groups_first_follow_and_exit_chains(self) -> None:
        round_results = [
            SimulationRoundResult(
                round_id="round-1",
                order=1,
                focus="Ignition",
                objective="Start the move",
                status="completed",
                participant_updates=[
                    SimulationParticipantUpdate(
                        participant_id="alpha",
                        action_type="init_buy",
                        action_name="INIT_BUY",
                        previous_state="ready",
                        next_state="engaged",
                        round_id="round-1",
                        reason_codes=["action:init_buy"],
                    ),
                    SimulationParticipantUpdate(
                        participant_id="beta",
                        action_type="add_buy",
                        action_name="ADD_BUY",
                        previous_state="ready",
                        next_state="monitoring",
                        round_id="round-1",
                        reason_codes=["action:add_buy"],
                    ),
                ],
                participant_states=[],
                reason_codes=["round:1"],
            ),
            SimulationRoundResult(
                round_id="round-4",
                order=4,
                focus="Risk Check",
                objective="Watch for exits",
                status="completed",
                participant_updates=[
                    SimulationParticipantUpdate(
                        participant_id="alpha",
                        action_type="exit",
                        action_name="EXIT",
                        previous_state="accelerating",
                        next_state="de_risking",
                        round_id="round-4",
                        reason_codes=["action:exit"],
                    )
                ],
                participant_states=[],
                reason_codes=["round:4"],
            ),
        ]

        timeline = build_simulation_timeline(round_results)

        self.assertEqual(timeline.status, "complete")
        self.assertEqual(len(timeline.first_move), 1)
        self.assertEqual(len(timeline.follow_on), 1)
        self.assertEqual(len(timeline.exit_chain), 1)
        self.assertIn("round-4", timeline.turning_points)

    def test_timeline_marks_incomplete_when_rounds_are_missing(self) -> None:
        timeline = build_simulation_timeline([])
        self.assertEqual(timeline.status, "timeline_incomplete")
        self.assertEqual(timeline.first_move, [])


if __name__ == "__main__":
    unittest.main()

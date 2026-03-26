from __future__ import annotations

from domain.belief_graph.service import BeliefGraphError, BeliefGraphService
from schemas.scenario import ScenarioCase
from schemas.scenario_engine import ScenarioEngineResult


class ScenarioEngineError(Exception):
    def __init__(self, *, code: str, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class ScenarioEngineService:
    def __init__(self, belief_graph: BeliefGraphService) -> None:
        self.belief_graph = belief_graph

    def build_scenarios(self, event_id: str) -> ScenarioEngineResult:
        try:
            snapshot = self.belief_graph.build_snapshot(event_id)
        except BeliefGraphError as exc:
            raise ScenarioEngineError(code=exc.code, message=exc.message, status_code=exc.status_code) from exc

        supporter_count = len(snapshot.key_supporters)
        opponent_count = len(snapshot.key_opponents)
        graph_metrics = {
            "participant_count": snapshot.participant_count,
            "supporter_count": supporter_count,
            "opponent_count": opponent_count,
            "consensus_signal_count": len(snapshot.consensus_signals),
            "divergence_signal_count": len(snapshot.divergence_signals),
            "graph_status": snapshot.status,
        }
        dominant = self._resolve_dominant_scenario(
            supporter_count=supporter_count,
            opponent_count=opponent_count,
            consensus_signal_count=len(snapshot.consensus_signals),
        )
        scenarios = [
            ScenarioCase(
                scenario_id="base",
                thesis="Base case follows the currently strongest confirmed transmission path.",
                first_movers=snapshot.key_supporters[:2],
                followers=snapshot.key_supporters[2:4] or snapshot.key_opponents[:1],
                watchpoints=snapshot.consensus_signals[:3] or ["watch graph confirmation"],
                invalidation_conditions=snapshot.divergence_signals[:3] or ["support breadth fades"],
                confidence=0.58 if snapshot.status == "built" else 0.44,
            ),
            ScenarioCase(
                scenario_id="bull",
                thesis="Bull case assumes supporters stay dominant and the signal broadens.",
                first_movers=snapshot.key_supporters[:2],
                followers=snapshot.key_supporters[2:4],
                watchpoints=(snapshot.consensus_signals[:2] + ["track first-mover expansion"])[:3],
                invalidation_conditions=snapshot.divergence_signals[:2] or ["opponents regain control"],
                confidence=0.72 if dominant == "bull" else 0.46,
            ),
            ScenarioCase(
                scenario_id="bear",
                thesis="Bear case assumes opposition or invalidation signals take control.",
                first_movers=snapshot.key_opponents[:2],
                followers=snapshot.key_opponents[2:4] or snapshot.key_supporters[:1],
                watchpoints=(snapshot.divergence_signals[:2] + ["track failed confirmation"])[:3],
                invalidation_conditions=snapshot.consensus_signals[:2] or ["support breadth re-accelerates"],
                confidence=0.68 if dominant == "bear" else 0.43,
            ),
        ]
        if snapshot.status == "empty":
            scenarios[1] = ScenarioCase(
                scenario_id="bull",
                thesis="Bull case stays constrained until the graph has enough evidence.",
                first_movers=[],
                followers=[],
                watchpoints=snapshot.consensus_signals[:3] or ["wait for stronger participant support"],
                invalidation_conditions=["evidence remains thin"],
                confidence=0.22,
            )
            scenarios[2] = ScenarioCase(
                scenario_id="bear",
                thesis="Bear case stays constrained until the graph shows stronger opposition.",
                first_movers=[],
                followers=[],
                watchpoints=snapshot.consensus_signals[:3] or ["wait for stronger negative confirmation"],
                invalidation_conditions=["evidence remains thin"],
                confidence=0.22,
            )
            dominant = "base"
        return ScenarioEngineResult(
            event_id=event_id,
            dominant_scenario=dominant,
            graph_status=snapshot.status,
            graph_metrics=graph_metrics,
            scenarios=scenarios,
        )

    def _resolve_dominant_scenario(
        self,
        *,
        supporter_count: int,
        opponent_count: int,
        consensus_signal_count: int,
    ) -> str:
        if supporter_count >= opponent_count + 2 and consensus_signal_count >= 1:
            return "bull"
        if opponent_count > supporter_count:
            return "bear"
        return "base"

    def preview_weight_feedback(self, recommendations: list[dict[str, object]]) -> list[dict[str, object]]:
        base_weights = {"bull": 0.5, "base": 0.5, "bear": 0.5}
        preview: list[dict[str, object]] = []
        for recommendation in recommendations:
            scenario_id = str(recommendation.get("scenario_id") or "base")
            current_weight = base_weights.get(scenario_id, 0.5)
            preview.append(
                {
                    "scenario_id": scenario_id,
                    "current_weight": current_weight,
                    "suggested_weight": round(float(recommendation.get("suggested_weight") or current_weight), 2),
                    "reason": str(recommendation.get("reason") or ""),
                }
            )
        return preview

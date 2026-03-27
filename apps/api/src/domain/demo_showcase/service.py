from __future__ import annotations

from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any

from schemas.demo_showcase import RuntimeShowcaseResponse


class DemoRuntimeShowcaseService:
    def __init__(
        self,
        *,
        repo_root: Path,
        event_runtime_root: Path,
        simulation_runtime_root: Path,
        statement_meta_root: Path,
        statement_parse_report_root: Path,
        trade_record_root: Path,
        statement_style_root: Path,
        roadmap_acceptance_root: Path,
    ) -> None:
        self.repo_root = repo_root
        self.event_runtime_root = event_runtime_root
        self.simulation_runtime_root = simulation_runtime_root
        self.statement_meta_root = statement_meta_root
        self.statement_parse_report_root = statement_parse_report_root
        self.trade_record_root = trade_record_root
        self.statement_style_root = statement_style_root
        self.roadmap_acceptance_root = roadmap_acceptance_root

    def build_showcase(self) -> RuntimeShowcaseResponse:
        event_demo = self._build_event_demo()
        statement_demo = self._build_statement_demo()
        acceptance_demo = self._build_acceptance_demo()
        return RuntimeShowcaseResponse(
            generated_at=datetime.now(UTC).isoformat(),
            event_demo=event_demo,
            statement_demo=statement_demo,
            acceptance_demo=acceptance_demo,
            source_paths={
                "event_demo": event_demo.get("source_paths", {}),
                "statement_demo": statement_demo.get("source_paths", {}),
                "acceptance_demo": acceptance_demo.get("source_paths", {}),
            },
        )

    def _build_event_demo(self) -> dict[str, Any]:
        record_path = self._latest_json(self.event_runtime_root / "records")
        if record_path is None:
            return self._missing_demo(
                kind="event_demo",
                message="暂无真实事件样例，先跑通 event -> simulation -> outcome 链后这里会自动出现。",
            )
        record = self._read_json(record_path)
        event_id = str(record.get("event_id") or "")
        structure_path = self.event_runtime_root / "structures" / f"{event_id}.json"
        mapping_path = self.event_runtime_root / "mappings" / f"{event_id}.json"
        casebook_path = self.event_runtime_root / "casebook" / f"{event_id}.json"
        simulation_path = self._latest_matching_json(self.simulation_runtime_root / "runs", f"{event_id}-*.json")
        outcome_path = self._latest_matching_json(self.event_runtime_root / "outcomes", f"{event_id}-*.json")
        structure = self._read_json(structure_path) if structure_path.exists() else {}
        mapping = self._read_json(mapping_path) if mapping_path.exists() else {}
        casebook = self._read_json(casebook_path) if casebook_path.exists() else {}
        simulation = self._read_json(simulation_path) if simulation_path is not None else {}
        outcome = self._read_json(outcome_path) if outcome_path is not None else {}
        top_participants = self._top_participants(simulation)
        timeline = self._timeline_summary(simulation)
        why = self._build_event_why(record=record, structure=structure, mapping=mapping, simulation=simulation, outcome=outcome)
        return {
            "status": "ready",
            "event_id": event_id,
            "headline": f"{record.get('title') or event_id}: {str(outcome.get('dominant_scenario_actual') or simulation.get('dominant_scenario') or 'pending').upper()}",
            "summary": {
                "title": record.get("title"),
                "body": record.get("body"),
                "event_time": record.get("event_time"),
                "event_type": structure.get("event_type"),
                "mapped_symbols": mapping.get("target_symbols") or mapping.get("symbols") or [],
                "dominant_scenario": simulation.get("dominant_scenario"),
                "actual_outcome": outcome.get("dominant_scenario_actual"),
                "score_label": outcome.get("score_label"),
            },
            "structure": {
                "event_type": structure.get("event_type"),
                "impact_direction": structure.get("impact_direction"),
                "affected_sector": structure.get("affected_sector"),
                "trigger_phrase": structure.get("trigger_phrase"),
                "watchpoints": structure.get("watchpoints") or casebook.get("watchpoints") or [],
                "invalidation_conditions": structure.get("invalidation_conditions") or [],
            },
            "mapping": {
                "primary_theme": mapping.get("primary_theme"),
                "target_symbols": mapping.get("target_symbols") or mapping.get("symbols") or [],
                "target_entities": mapping.get("target_entities") or [],
                "theme_rationale": mapping.get("theme_rationale") or [],
            },
            "simulation": {
                "run_id": simulation.get("run_id"),
                "status": simulation.get("status", "missing"),
                "dominant_scenario": simulation.get("dominant_scenario"),
                "round_count": simulation.get("round_count"),
                "timeline": timeline,
                "watchpoints": simulation.get("watchpoints") or [],
                "top_participants": top_participants,
                "action_log_path": simulation.get("action_log_path"),
            },
            "outcome": {
                "status": outcome.get("status", "missing"),
                "horizon": outcome.get("horizon"),
                "dominant_scenario_actual": outcome.get("dominant_scenario_actual"),
                "score_label": outcome.get("score_label"),
                "sector_performance": outcome.get("sector_performance"),
                "leader_performance": outcome.get("leader_performance"),
                "supporting_evidence": outcome.get("supporting_evidence") or [],
            },
            "why": why,
            "source_paths": {
                "record": str(record_path),
                "structure": str(structure_path) if structure_path.exists() else "",
                "mapping": str(mapping_path) if mapping_path.exists() else "",
                "casebook": str(casebook_path) if casebook_path.exists() else "",
                "simulation": str(simulation_path) if simulation_path is not None else "",
                "outcome": str(outcome_path) if outcome_path is not None else "",
            },
        }

    def _build_statement_demo(self) -> dict[str, Any]:
        statement_path = self._latest_json(self.statement_meta_root)
        if statement_path is None:
            return self._missing_demo(
                kind="statement_demo",
                message="暂无真实 statement 样例，先跑 statement style / mirror 链后这里会自动出现。",
            )
        metadata = self._read_json(statement_path)
        statement_id = str(metadata.get("statement_id") or "")
        parse_report_path = self.statement_parse_report_root / f"{statement_id}.json"
        trade_record_path = self.trade_record_root / f"{statement_id}.json"
        style_features_path = self.statement_style_root / "features" / f"{statement_id}.json"
        mirror_agent_path = self.statement_style_root / "mirror_agents" / f"{statement_id}.json"
        mirror_validation_path = self.statement_style_root / "mirror_validation" / f"{statement_id}.json"
        distribution_calibration_path = self.statement_style_root / "distribution_calibration" / f"{statement_id}.json"
        parse_report = self._read_json(parse_report_path) if parse_report_path.exists() else {}
        trade_record = self._read_json(trade_record_path) if trade_record_path.exists() else {}
        style_features = self._read_json(style_features_path) if style_features_path.exists() else {}
        mirror_agent = self._read_json(mirror_agent_path) if mirror_agent_path.exists() else {}
        mirror_validation = self._read_json(mirror_validation_path) if mirror_validation_path.exists() else {}
        distribution_calibration = self._read_json(distribution_calibration_path) if distribution_calibration_path.exists() else {}
        return {
            "status": "ready",
            "statement_id": statement_id,
            "headline": f"{statement_id}: {mirror_agent.get('participant_family') or 'mirror pending'} / {mirror_agent.get('archetype_name') or 'style pending'}",
            "summary": {
                "statement_id": statement_id,
                "owner_id": metadata.get("owner_id"),
                "market": metadata.get("market"),
                "file_name": metadata.get("file_name"),
                "upload_status": metadata.get("upload_status"),
                "detected_file_type": metadata.get("detected_file_type"),
            },
            "parse_report": {
                "status": parse_report.get("status", "missing"),
                "parser_key": parse_report.get("parser_key"),
                "account_name": parse_report.get("account_name"),
                "trade_count": parse_report.get("trade_count"),
                "date_span": parse_report.get("date_span") or {},
            },
            "trade_sample": self._trade_sample(trade_record),
            "style_features": {
                "status": style_features.get("status", "missing"),
                "trade_count": style_features.get("trade_count"),
                "feature_vector": style_features.get("feature_vector") or {},
                "style_summary": style_features.get("style_summary") or {},
            },
            "mirror_agent": {
                "status": mirror_agent.get("status", "missing"),
                "archetype_name": mirror_agent.get("archetype_name"),
                "participant_family": mirror_agent.get("participant_family"),
                "profile": mirror_agent.get("profile") or {},
                "evidence": mirror_agent.get("evidence") or [],
            },
            "mirror_validation": {
                "status": mirror_validation.get("status", "missing"),
                "grading": mirror_validation.get("grading"),
                "risk_posture": mirror_validation.get("risk_posture"),
                "consistency_score": mirror_validation.get("consistency_score"),
                "notes": mirror_validation.get("notes") or [],
            },
            "distribution_calibration": {
                "status": distribution_calibration.get("status", "missing"),
                "sample_size": distribution_calibration.get("sample_size"),
                "hit_rate": distribution_calibration.get("hit_rate"),
                "segments": distribution_calibration.get("segments") or [],
            },
            "source_paths": {
                "statement": str(statement_path),
                "parse_report": str(parse_report_path) if parse_report_path.exists() else "",
                "trade_record": str(trade_record_path) if trade_record_path.exists() else "",
                "style_features": str(style_features_path) if style_features_path.exists() else "",
                "mirror_agent": str(mirror_agent_path) if mirror_agent_path.exists() else "",
                "mirror_validation": str(mirror_validation_path) if mirror_validation_path.exists() else "",
                "distribution_calibration": str(distribution_calibration_path) if distribution_calibration_path.exists() else "",
            },
        }

    def _build_acceptance_demo(self) -> dict[str, Any]:
        acceptance_path = self.roadmap_acceptance_root / "roadmap_1_6.json"
        if not acceptance_path.exists():
            return self._missing_demo(
                kind="acceptance_demo",
                message="暂无 acceptance pack，跑完 roadmap acceptance 后这里会自动出现。",
            )
        pack = self._read_json(acceptance_path)
        delivery_artifacts = pack.get("delivery_artifacts") or []
        return {
            "status": "ready",
            "roadmap_id": pack.get("roadmap_id", "roadmap_1_6"),
            "headline": pack.get("headline") or "Roadmap 1.6 acceptance pack",
            "p0_boundaries": pack.get("p0_boundaries") or [],
            "p1_boundaries": pack.get("p1_boundaries") or [],
            "current_handoff": pack.get("current_handoff") or {},
            "delivery_artifacts": delivery_artifacts[:8],
            "summary": {
                "status": pack.get("status"),
                "p0_count": len(pack.get("p0_boundaries") or []),
                "p1_count": len(pack.get("p1_boundaries") or []),
                "delivery_artifact_count": len(delivery_artifacts),
            },
            "source_paths": {"acceptance_pack": str(acceptance_path)},
        }

    def _missing_demo(self, *, kind: str, message: str) -> dict[str, Any]:
        return {
            "status": "missing",
            kind[:-5] + "_id" if kind.endswith("_demo") else "id": "",
            "headline": "暂无真实样例",
            "summary": {"message": message},
            "source_paths": {},
        }

    def _build_event_why(
        self,
        *,
        record: dict[str, Any],
        structure: dict[str, Any],
        mapping: dict[str, Any],
        simulation: dict[str, Any],
        outcome: dict[str, Any],
    ) -> dict[str, Any]:
        dominant = str(simulation.get("dominant_scenario") or "pending")
        actual = str(outcome.get("dominant_scenario_actual") or "pending")
        score = str(outcome.get("score_label") or "pending")
        supporters = [item.get("participant_id") for item in self._top_participants(simulation)[:2] if item.get("participant_id")]
        turning_points = ((simulation.get("timeline") or {}).get("turning_points") or []) if isinstance(simulation.get("timeline"), dict) else []
        mapped_symbols = mapping.get("target_symbols") or mapping.get("symbols") or []
        answer_parts = [
            f"事件 {record.get('event_id') or record.get('title') or 'unknown'} 被识别为 {structure.get('event_type') or 'unknown'}，主推演场景是 {dominant}。",
            f"映射资产集中在 {', '.join(mapped_symbols[:3]) or '待补齐'}，重点参与者包括 {', '.join(supporters) or '待补齐'}。",
        ]
        if turning_points:
            answer_parts.append(f"模拟转折点出现在 {', '.join(str(item) for item in turning_points[:3])}。")
        if outcome:
            answer_parts.append(f"最终实际 outcome 为 {actual}，评分标签是 {score}。")
        else:
            answer_parts.append("目前还没有落盘 outcome，所以这里只展示推演侧结果。")
        return {
            "status": "ready" if simulation else "missing",
            "answer": " ".join(answer_parts),
            "supporters": supporters,
            "turning_points": turning_points,
        }

    def _top_participants(self, simulation: dict[str, Any]) -> list[dict[str, Any]]:
        participants = simulation.get("participant_states") if isinstance(simulation.get("participant_states"), list) else []
        ordered = sorted(
            [item for item in participants if isinstance(item, dict)],
            key=lambda item: float(item.get("authority_weight") or 0),
            reverse=True,
        )
        return [
            {
                "participant_id": item.get("participant_id"),
                "participant_family": item.get("participant_family"),
                "role": item.get("role"),
                "stance": item.get("stance"),
                "authority_weight": item.get("authority_weight"),
                "state": item.get("state"),
            }
            for item in ordered[:5]
        ]

    def _timeline_summary(self, simulation: dict[str, Any]) -> dict[str, Any]:
        timeline = simulation.get("timeline") if isinstance(simulation.get("timeline"), dict) else {}
        first_move = timeline.get("first_move") or []
        follow_on = timeline.get("follow_on") or []
        return {
            "status": timeline.get("status", "missing"),
            "turning_points": timeline.get("turning_points") or [],
            "first_move": first_move[:3] if isinstance(first_move, list) else [],
            "follow_on": follow_on[:3] if isinstance(follow_on, list) else [],
        }

    def _trade_sample(self, trade_record: dict[str, Any] | list[Any]) -> dict[str, Any]:
        if isinstance(trade_record, list):
            trades = trade_record
            return {
                "status": "ready" if trades else "missing",
                "trade_count": len(trades),
                "sample": trades[:5],
            }

        trades = trade_record.get("trades") if isinstance(trade_record.get("trades"), list) else []
        return {
            "status": trade_record.get("status", "missing"),
            "trade_count": trade_record.get("trade_count", len(trades)),
            "sample": trades[:5],
        }

    def _latest_json(self, root: Path) -> Path | None:
        if not root.exists():
            return None
        candidates = [path for path in root.glob("*.json") if path.is_file()]
        if not candidates:
            return None
        return max(candidates, key=lambda path: path.stat().st_mtime)

    def _latest_matching_json(self, root: Path, pattern: str) -> Path | None:
        if not root.exists():
            return None
        candidates = [path for path in root.glob(pattern) if path.is_file()]
        if not candidates:
            return None
        return max(candidates, key=lambda path: path.stat().st_mtime)

    def _read_json(self, path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))

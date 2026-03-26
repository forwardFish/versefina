from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path

from domain.mirror_agent.validation import validate_mirror_agent
from domain.style_embedding.service import StyleEmbeddingError, StyleEmbeddingService
from schemas.mirror_agent import MirrorAgent, MirrorAgentValidation


class MirrorAgentError(Exception):
    def __init__(self, *, code: str, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class MirrorAgentService:
    def __init__(self, *, style_root: Path, style_embedding_service: StyleEmbeddingService) -> None:
        self.style_root = style_root
        self.style_embedding_service = style_embedding_service
        self.mirror_root = style_root / "mirror_agents"
        self.validation_root = style_root / "mirror_validation"
        self.mirror_root.mkdir(parents=True, exist_ok=True)
        self.validation_root.mkdir(parents=True, exist_ok=True)

    def build_mirror_agent(self, statement_id: str) -> MirrorAgent:
        try:
            style_embedding = self.style_embedding_service.load_market_style_embedding(statement_id) or self.style_embedding_service.build_market_style_embedding(statement_id)
            archetype_seed = self.style_embedding_service.load_archetype_seed(statement_id) or self.style_embedding_service.build_archetype_seed(statement_id)
            activation_calibration = self.style_embedding_service.load_activation_calibration(statement_id) or self.style_embedding_service.build_activation_calibration(statement_id)
        except StyleEmbeddingError as exc:
            raise MirrorAgentError(code=exc.code, message=exc.message, status_code=exc.status_code) from exc

        agent = MirrorAgent(
            statement_id=statement_id,
            status="partial" if style_embedding.low_confidence else "ready",
            archetype_name=archetype_seed.archetype_name,
            participant_family=archetype_seed.participant_family,
            style_embedding=style_embedding.to_dict(),
            activation_calibration=activation_calibration.to_dict(),
            profile={
                "participant_family": archetype_seed.participant_family,
                "archetype_name": archetype_seed.archetype_name,
                "secondary_entry_only": True,
                "style_tags": [
                    str(style_embedding.reaction_latency_profile.get("label") or "medium"),
                    archetype_seed.archetype_name,
                ],
            },
            evidence=[
                "style_embedding",
                "archetype_seed",
                "activation_calibration",
            ],
        )
        self._persist(self.mirror_root, statement_id, asdict(agent))
        return agent

    def load_mirror_agent(self, statement_id: str) -> MirrorAgent | None:
        payload = self._load_payload(self.mirror_root, statement_id)
        return MirrorAgent(**payload) if payload is not None else None

    def validate_mirror_agent(self, statement_id: str) -> MirrorAgentValidation:
        agent = self.load_mirror_agent(statement_id) or self.build_mirror_agent(statement_id)
        validation = validate_mirror_agent(agent)
        self._persist(self.validation_root, statement_id, asdict(validation))
        return validation

    def load_mirror_validation(self, statement_id: str) -> MirrorAgentValidation | None:
        payload = self._load_payload(self.validation_root, statement_id)
        return MirrorAgentValidation(**payload) if payload is not None else None

    def _persist(self, root: Path, statement_id: str, payload: dict[str, object]) -> None:
        target_path = root / f"{statement_id}.json"
        target_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _load_payload(self, root: Path, statement_id: str) -> dict[str, object] | None:
        target_path = root / f"{statement_id}.json"
        if not target_path.exists():
            return None
        return json.loads(target_path.read_text(encoding="utf-8"))

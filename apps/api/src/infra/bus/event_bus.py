from __future__ import annotations


def publish_event(name: str, payload: dict[str, str]) -> dict[str, object]:
    return {"event": name, "payload": payload}

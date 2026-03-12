from __future__ import annotations


def audit_event(action: str, trace_id: str) -> dict[str, str]:
    return {"action": action, "trace_id": trace_id}

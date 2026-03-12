from __future__ import annotations


def build_daily_simulation_graph() -> dict[str, list[str]]:
    return {"name": "daily_simulation", "nodes": ["context", "plan", "act", "audit", "explain"]}

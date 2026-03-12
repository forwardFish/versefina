from __future__ import annotations


def build_review_graph() -> dict[str, list[str]]:
    return {"name": "review", "nodes": ["ingest", "learn", "audit", "explain"]}

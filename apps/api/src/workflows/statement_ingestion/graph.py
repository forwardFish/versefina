from __future__ import annotations


def build_statement_ingestion_graph() -> dict[str, list[str]]:
    return {"name": "statement_ingestion", "nodes": ["ingest", "normalize", "audit"]}

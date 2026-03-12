from __future__ import annotations


def shard_strategy() -> str:
    return "hash(agent_id)%N"

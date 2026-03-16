from __future__ import annotations


STATEMENT_STATUS_UPLOADED = "uploaded"
STATEMENT_STATUS_PARSING = "parsing"
STATEMENT_STATUS_PARSED = "parsed"
STATEMENT_STATUS_FAILED = "failed"

ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    STATEMENT_STATUS_UPLOADED: {STATEMENT_STATUS_PARSING, STATEMENT_STATUS_FAILED},
    STATEMENT_STATUS_PARSING: {STATEMENT_STATUS_PARSED, STATEMENT_STATUS_FAILED},
    STATEMENT_STATUS_PARSED: set(),
    STATEMENT_STATUS_FAILED: set(),
}


class InvalidStatementTransitionError(ValueError):
    pass


def validate_statement_transition(current_status: str, next_status: str) -> None:
    allowed = ALLOWED_TRANSITIONS.get(current_status, set())
    if next_status not in allowed:
        raise InvalidStatementTransitionError(
            f"Illegal statement status transition: {current_status} -> {next_status}"
        )

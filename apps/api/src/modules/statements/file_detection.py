from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ALLOWED_FILE_TYPES = {
    ".csv": {
        "detected_file_type": "csv",
        "parser_key": "statement_csv_parser",
        "allowed_content_types": {"text/csv", "application/csv", "application/vnd.ms-excel", "application/octet-stream"},
    },
    ".xls": {
        "detected_file_type": "xls",
        "parser_key": "statement_excel_parser",
        "allowed_content_types": {"application/vnd.ms-excel", "application/octet-stream"},
    },
    ".xlsx": {
        "detected_file_type": "xlsx",
        "parser_key": "statement_excel_parser",
        "allowed_content_types": {
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/zip",
            "application/octet-stream",
        },
    },
}


class StatementFileDetectionError(ValueError):
    def __init__(self, *, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True, slots=True)
class FileDetectionResult:
    detected_file_type: str
    parser_key: str
    normalized_content_type: str


def detect_statement_file_type(*, file_name: str, content_type: str) -> FileDetectionResult:
    suffix = Path(file_name).suffix.lower()
    definition = ALLOWED_FILE_TYPES.get(suffix)
    if definition is None:
        raise StatementFileDetectionError(
            code="STATEMENT_FILE_TYPE_UNSUPPORTED",
            message="Only .csv, .xls, and .xlsx statement files are supported.",
        )

    normalized_content_type = (content_type or "application/octet-stream").lower()
    if normalized_content_type not in definition["allowed_content_types"]:
        raise StatementFileDetectionError(
            code="STATEMENT_FILE_TYPE_MISMATCH",
            message=(
                f"File extension {suffix} does not match content type {normalized_content_type}. "
                "Please upload a file with a consistent extension and MIME type."
            ),
        )

    return FileDetectionResult(
        detected_file_type=definition["detected_file_type"],
        parser_key=definition["parser_key"],
        normalized_content_type=normalized_content_type,
    )

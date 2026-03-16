from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path

import pandas as pd

from infra.storage.object_store import LocalObjectStore
from modules.statements.mappers import detect_mapping_rule, map_row_to_canonical
from schemas.command import StatementMetadata, StatementParseResponse
from schemas.trade import TradeRecord


@dataclass(frozen=True, slots=True)
class ParseIssue:
    row_number: int
    error_code: str
    message: str


class StatementParseError(ValueError):
    def __init__(self, *, code: str, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class StatementParseService:
    def __init__(self, *, object_store: LocalObjectStore, parse_report_root: Path, trade_record_root: Path) -> None:
        self.object_store = object_store
        self.parse_report_root = parse_report_root
        self.trade_record_root = trade_record_root
        self.parse_report_root.mkdir(parents=True, exist_ok=True)
        self.trade_record_root.mkdir(parents=True, exist_ok=True)

    def parse_statement(self, metadata: StatementMetadata) -> StatementParseResponse:
        source = Path(self.object_store.root) / metadata.bucket / Path(metadata.object_key)
        if not source.exists():
            raise StatementParseError(
                code="STATEMENT_SOURCE_NOT_FOUND",
                message="Uploaded statement object does not exist in storage.",
                status_code=404,
            )

        frame = self._load_dataframe(source, metadata.detected_file_type)
        if frame.empty:
            raise StatementParseError(
                code="STATEMENT_PARSE_EMPTY",
                message="Uploaded statement does not contain any rows to parse.",
            )

        try:
            mapping_rule = detect_mapping_rule(list(frame.columns))
        except ValueError as exc:
            raise StatementParseError(
                code="STATEMENT_MAPPING_RULE_NOT_FOUND",
                message=str(exc),
            ) from exc

        return self._normalize_and_persist(metadata, frame, mapping_rule)

    def _load_dataframe(self, source: Path, detected_file_type: str) -> pd.DataFrame:
        if detected_file_type == "csv":
            return self._load_text_dataframe(source)
        if detected_file_type == "xls":
            try:
                return pd.read_excel(source, engine="xlrd")
            except Exception:
                return self._load_text_dataframe(source)
        if detected_file_type == "xlsx":
            try:
                return pd.read_excel(source, engine="openpyxl")
            except Exception:
                return self._load_text_dataframe(source)
        raise StatementParseError(
            code="STATEMENT_PARSE_FORMAT_UNSUPPORTED",
            message=f"Unsupported parsed file type: {detected_file_type}",
        )

    def _load_text_dataframe(self, source: Path) -> pd.DataFrame:
        encodings = ["utf-8-sig", "gb18030", "gbk"]
        last_error: Exception | None = None
        for encoding in encodings:
            try:
                return pd.read_csv(source, sep=None, engine="python", encoding=encoding)
            except Exception as exc:
                last_error = exc
        raise StatementParseError(
            code="STATEMENT_PARSE_TEXT_FAILED",
            message=f"Unable to parse statement as delimited text: {last_error}",
        )

    def _normalize_and_persist(self, metadata: StatementMetadata, frame: pd.DataFrame, mapping_rule) -> StatementParseResponse:
        records: list[TradeRecord] = []
        issues: list[ParseIssue] = []
        rows = frame.to_dict(orient="records")
        for row_number, row in enumerate(rows, start=1):
            try:
                canonical = map_row_to_canonical(row, mapping_rule)
                records.append(
                    TradeRecord(
                        statement_id=metadata.statement_id,
                        traded_at=self._normalize_datetime(canonical["traded_at"]),
                        symbol=self._normalize_symbol(canonical["symbol"]),
                        side=self._normalize_side(canonical["side"]),
                        qty=self._normalize_int(canonical["qty"], field_name="qty"),
                        price=self._normalize_float(canonical["price"], field_name="price"),
                        fee=self._normalize_float(canonical.get("fee", 0), field_name="fee"),
                        tax=self._normalize_float(canonical.get("tax", 0), field_name="tax"),
                        broker=mapping_rule.broker,
                        row_number=row_number,
                    )
                )
            except StatementParseError as exc:
                issues.append(ParseIssue(row_number=row_number, error_code=exc.code, message=exc.message))

        report_path = self.parse_report_root / f"{metadata.statement_id}.json"
        records_path = self.trade_record_root / f"{metadata.statement_id}.json"
        records_path.write_text(
            json.dumps([asdict(record) for record in records], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        report = {
            "statement_id": metadata.statement_id,
            "broker": mapping_rule.broker,
            "detected_file_type": metadata.detected_file_type,
            "parser_key": metadata.parser_key,
            "total_rows": len(rows),
            "parsed_records": len(records),
            "failed_records": len(issues),
            "issues": [asdict(issue) for issue in issues],
            "trade_record_path": str(records_path),
        }
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        return StatementParseResponse(
            statement_id=metadata.statement_id,
            upload_status="parsed" if not issues else "failed",
            parsed_records=len(records),
            failed_records=len(issues),
            parse_report_path=str(report_path),
            trade_record_path=str(records_path),
            error_code=None if not issues else "STATEMENT_PARSE_PARTIAL_FAILURE",
            error_message=None if not issues else "Some statement rows failed to parse.",
        )

    def _normalize_side(self, value: object) -> str:
        text = str(value).strip().lower()
        if text in {"buy", "b", "买入", "证券买入"}:
            return "buy"
        if text in {"sell", "s", "卖出", "证券卖出"}:
            return "sell"
        raise StatementParseError(code="STATEMENT_SIDE_INVALID", message=f"Unsupported trade side: {value}")

    def _normalize_symbol(self, value: object) -> str:
        text = str(value).strip()
        if not text:
            raise StatementParseError(code="STATEMENT_SYMBOL_MISSING", message="Trade symbol is required.")
        if text.isdigit() and len(text) <= 6:
            digits = text.zfill(6)
            if digits.startswith(("5", "6", "9")):
                return f"{digits}.SH"
            return f"{digits}.SZ"
        return text

    def _normalize_datetime(self, value: object) -> str:
        text = str(value).strip()
        if not text:
            raise StatementParseError(code="STATEMENT_TRADE_DATE_MISSING", message="Trade date is required.")
        if text.isdigit() and len(text) == 8:
            return f"{text[:4]}-{text[4:6]}-{text[6:]}"
        return text

    def _normalize_int(self, value: object, *, field_name: str) -> int:
        try:
            return int(float(value))
        except Exception as exc:
            raise StatementParseError(
                code=f"STATEMENT_{field_name.upper()}_INVALID",
                message=f"{field_name} must be a number.",
            ) from exc

    def _normalize_float(self, value: object, *, field_name: str) -> float:
        if value in (None, "", "nan"):
            return 0.0
        try:
            return float(value)
        except Exception as exc:
            raise StatementParseError(
                code=f"STATEMENT_{field_name.upper()}_INVALID",
                message=f"{field_name} must be numeric.",
            ) from exc

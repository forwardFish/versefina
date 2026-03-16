from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MappingRule:
    broker: str
    required_columns: tuple[str, ...]
    aliases: dict[str, str]


BROKER_RULES: tuple[MappingRule, ...] = (
    MappingRule(
        broker="generic_cn_broker",
        required_columns=("成交日期", "证券代码", "买卖方向", "成交数量", "成交价格"),
        aliases={
            "traded_at": "成交日期",
            "symbol": "证券代码",
            "side": "买卖方向",
            "qty": "成交数量",
            "price": "成交价格",
            "fee": "手续费",
            "tax": "印花税",
        },
    ),
    MappingRule(
        broker="generic_en_broker",
        required_columns=("trade_date", "symbol", "side", "quantity", "price"),
        aliases={
            "traded_at": "trade_date",
            "symbol": "symbol",
            "side": "side",
            "qty": "quantity",
            "price": "price",
            "fee": "fee",
            "tax": "tax",
        },
    ),
)


class MappingRuleError(ValueError):
    pass


def detect_mapping_rule(columns: list[str]) -> MappingRule:
    column_set = {_normalize_column_name(column) for column in columns}
    for rule in BROKER_RULES:
        if {_normalize_column_name(column) for column in rule.required_columns}.issubset(column_set):
            return rule
    raise MappingRuleError(
        "No supported statement mapping rule matched the uploaded file columns."
    )


def map_row_to_canonical(row: dict[str, object], rule: MappingRule) -> dict[str, object]:
    canonical: dict[str, object] = {}
    normalized_row = {_normalize_column_name(key): value for key, value in row.items()}
    for target_field, source_column in rule.aliases.items():
        canonical[target_field] = normalized_row.get(_normalize_column_name(source_column))
    return canonical


def _normalize_column_name(value: object) -> str:
    return str(value).replace("\ufeff", "").strip()

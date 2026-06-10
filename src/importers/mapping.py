from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher
from typing import Iterable

import pandas as pd


STANDARD_FIELDS = (
    "asin",
    "title",
    "brand",
    "price",
    "rating",
    "reviews",
    "monthly_sales",
    "category",
)
REQUIRED_FIELDS = frozenset(STANDARD_FIELDS)

FIELD_LABELS = {
    "asin": "ASIN",
    "title": "Title",
    "brand": "Brand",
    "price": "Price",
    "rating": "Rating",
    "reviews": "Reviews",
    "monthly_sales": "Monthly Sales",
    "category": "Category",
}

FIELD_ALIASES = {
    "asin": (
        "asin",
        "product asin",
        "item asin",
        "产品asin",
        "商品asin",
    ),
    "title": (
        "title",
        "product title",
        "product name",
        "item name",
        "产品名称",
        "商品名称",
        "标题",
    ),
    "brand": (
        "brand",
        "brand name",
        "品牌",
        "品牌名称",
    ),
    "price": (
        "price",
        "current price",
        "sale price",
        "selling price",
        "售价",
        "价格",
        "当前价格",
    ),
    "rating": (
        "rating",
        "star rating",
        "stars",
        "average rating",
        "评分",
        "星级",
    ),
    "reviews": (
        "reviews",
        "review count",
        "ratings count",
        "number of reviews",
        "评论数",
        "评价数量",
        "评论数量",
    ),
    "monthly_sales": (
        "monthly sales",
        "monthly units",
        "estimated sales",
        "estimated monthly sales",
        "月销量",
        "预估月销量",
        "月销售量",
    ),
    "category": (
        "category",
        "product category",
        "product type",
        "类目",
        "分类",
        "产品分类",
    ),
}


class FieldMappingError(ValueError):
    """Raised when a column mapping is incomplete or ambiguous."""


def normalize_header(value: object) -> str:
    text = unicodedata.normalize("NFKC", str(value)).strip().lower()
    return re.sub(r"[\W_]+", "", text, flags=re.UNICODE)


def _candidate_score(standard_field: str, source_column: str) -> float:
    normalized_source = normalize_header(source_column)
    aliases = (standard_field, *FIELD_ALIASES[standard_field])
    normalized_aliases = {normalize_header(alias) for alias in aliases}

    if normalized_source in normalized_aliases:
        return 1.0

    return max(
        SequenceMatcher(None, normalized_source, alias).ratio()
        for alias in normalized_aliases
        if alias
    )


def suggest_field_mappings(
    columns: Iterable[object],
    fuzzy_threshold: float = 0.78,
) -> dict[str, str | None]:
    source_columns = [str(column) for column in columns]
    suggestions: dict[str, str | None] = {
        field: None for field in STANDARD_FIELDS
    }
    available = set(source_columns)

    scored: list[tuple[float, str, str]] = []
    for field in STANDARD_FIELDS:
        for column in source_columns:
            score = _candidate_score(field, column)
            if score >= fuzzy_threshold:
                scored.append((score, field, column))

    for score, field, column in sorted(
        scored,
        key=lambda item: (-item[0], STANDARD_FIELDS.index(item[1]), item[2]),
    ):
        if suggestions[field] is None and column in available:
            suggestions[field] = column
            available.remove(column)

    return suggestions


def validate_field_mapping(
    mapping: dict[str, str | None],
    source_columns: Iterable[object],
) -> None:
    columns = {str(column) for column in source_columns}
    missing = sorted(
        field
        for field in REQUIRED_FIELDS
        if not mapping.get(field)
    )
    if missing:
        raise FieldMappingError(
            "Required fields are not mapped: " + ", ".join(missing)
        )

    unknown_fields = sorted(set(mapping) - set(STANDARD_FIELDS))
    if unknown_fields:
        raise FieldMappingError(
            "Unknown standard fields: " + ", ".join(unknown_fields)
        )

    assigned = [str(value) for value in mapping.values() if value]
    missing_columns = sorted(set(assigned) - columns)
    if missing_columns:
        raise FieldMappingError(
            "Mapped source columns do not exist: " + ", ".join(missing_columns)
        )

    duplicates = sorted(
        column for column in set(assigned) if assigned.count(column) > 1
    )
    if duplicates:
        raise FieldMappingError(
            "Each source column can only be assigned once: "
            + ", ".join(duplicates)
        )


def apply_field_mapping(
    frame: pd.DataFrame,
    mapping: dict[str, str | None],
) -> pd.DataFrame:
    validate_field_mapping(mapping, frame.columns)
    selected = {
        str(source_column): standard_field
        for standard_field, source_column in mapping.items()
        if source_column
    }
    return frame.loc[:, list(selected)].rename(columns=selected).copy()

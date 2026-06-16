from __future__ import annotations

from typing import Any, Iterable

import pandas as pd

from .fields import get_spec_field, list_spec_fields


def _records(value: pd.DataFrame | list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    if value is None:
        return []
    if isinstance(value, pd.DataFrame):
        return value.to_dict("records")
    return list(value or [])


def _ordered_fields(fields: Iterable[str] | None = None) -> list[str]:
    if fields is not None:
        return list(dict.fromkeys(str(field) for field in fields if str(field).strip()))
    return [field.standard_field for field in list_spec_fields()]


def _total_product_urls(
    normalized_rows: list[dict[str, Any]],
    product_rows: list[dict[str, Any]],
) -> list[str]:
    urls: list[str] = []

    for row in product_rows:
        source_url = str(row.get("source_url", "")).strip()
        if source_url:
            urls.append(source_url)

    if not urls:
        for row in normalized_rows:
            source_url = str(row.get("source_url", "")).strip()
            if source_url:
                urls.append(source_url)

    return list(dict.fromkeys(urls))


def build_coverage_summary(
    normalized_specs: pd.DataFrame | list[dict[str, Any]],
    *,
    products: pd.DataFrame | list[dict[str, Any]] | None = None,
    fields: Iterable[str] | None = None,
    language: str = "en",
) -> pd.DataFrame:
    """Calculate per-field specification coverage.

    Coverage is calculated by counting unique product URLs that have a non-empty
    normalized value for each standard field.
    """

    spec_rows = _records(normalized_specs)
    product_rows = _records(products)
    product_urls = _total_product_urls(spec_rows, product_rows)
    total_products = len(product_urls)

    field_order = _ordered_fields(fields)
    urls_by_field: dict[str, set[str]] = {field: set() for field in field_order}

    for row in spec_rows:
        source_url = str(row.get("source_url", "")).strip()
        standard_field = str(row.get("standard_field", "")).strip()
        normalized_value = str(row.get("normalized_value", "") or "").strip()

        if not source_url or not standard_field or not normalized_value:
            continue

        if standard_field not in urls_by_field:
            urls_by_field[standard_field] = set()
            field_order.append(standard_field)

        urls_by_field[standard_field].add(source_url)

    rows: list[dict[str, Any]] = []
    for standard_field in field_order:
        product_count = len(urls_by_field.get(standard_field, set()))
        try:
            field = get_spec_field(standard_field)
            label = field.label(language)
            category = field.category
        except KeyError:
            label = standard_field
            category = "custom"

        coverage_rate = (product_count / total_products) if total_products else 0.0
        rows.append(
            {
                "standard_field": standard_field,
                "standard_label": label,
                "category": category,
                "products_with_value": product_count,
                "total_products": total_products,
                "coverage_rate": round(coverage_rate, 4),
            }
        )

    return pd.DataFrame(
        rows,
        columns=[
            "standard_field",
            "standard_label",
            "category",
            "products_with_value",
            "total_products",
            "coverage_rate",
        ],
    )

from __future__ import annotations

from collections import defaultdict
from typing import Iterable, Any

import pandas as pd

from .fields import list_spec_fields


BASE_COLUMNS = ["source_url", "title", "brand", "model"]


def matrix_field_columns(fields: Iterable[str] | None = None) -> list[str]:
    """Return ordered specification columns for a product-by-field matrix."""

    if fields is not None:
        return list(dict.fromkeys(str(field) for field in fields if str(field).strip()))

    return [field.standard_field for field in list_spec_fields()]


def _records(value: pd.DataFrame | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(value, pd.DataFrame):
        return value.to_dict("records")
    return list(value or [])


def _product_metadata(products: pd.DataFrame | list[dict[str, Any]] | None) -> dict[str, dict[str, str]]:
    metadata: dict[str, dict[str, str]] = {}
    if products is None:
        return metadata

    for row in _records(products):
        source_url = str(row.get("source_url", "")).strip()
        if not source_url:
            continue
        metadata[source_url] = {
            "title": str(row.get("title", "") or "").strip(),
            "brand": str(row.get("brand", "") or "").strip(),
            "model": str(row.get("model", "") or "").strip(),
        }

    return metadata


def _choose_value(existing: dict[str, Any] | None, candidate: dict[str, Any]) -> dict[str, Any]:
    """Choose the better normalized spec value for the matrix.

    Higher confidence wins. If confidence ties, prefer the longer non-empty value
    because it usually preserves more supplier evidence.
    """

    if existing is None:
        return candidate

    existing_confidence = float(existing.get("confidence") or 0)
    candidate_confidence = float(candidate.get("confidence") or 0)
    if candidate_confidence > existing_confidence:
        return candidate

    if candidate_confidence == existing_confidence:
        existing_value = str(existing.get("normalized_value") or "")
        candidate_value = str(candidate.get("normalized_value") or "")
        if len(candidate_value) > len(existing_value):
            return candidate

    return existing


def build_specification_matrix(
    normalized_specs: pd.DataFrame | list[dict[str, Any]],
    *,
    products: pd.DataFrame | list[dict[str, Any]] | None = None,
    fields: Iterable[str] | None = None,
) -> pd.DataFrame:
    """Build a product-by-standard-specification matrix.

    Parameters
    ----------
    normalized_specs:
        Rows produced by the normalized specification layer. Expected fields
        include ``source_url``, ``standard_field``, ``normalized_value`` and
        optionally ``confidence``.
    products:
        Optional product rows used to add title, brand and model metadata.
    fields:
        Optional standard-field order. When omitted, all known specification
        fields are included in dictionary order.

    Returns
    -------
    pandas.DataFrame
        One row per product URL and one column per standard specification field.
    """

    spec_rows = _records(normalized_specs)
    metadata = _product_metadata(products)
    field_columns = matrix_field_columns(fields)

    urls = list(metadata.keys())
    for row in spec_rows:
        source_url = str(row.get("source_url", "")).strip()
        if source_url and source_url not in urls:
            urls.append(source_url)

    selected: dict[tuple[str, str], dict[str, Any]] = {}
    extra_values: dict[tuple[str, str], list[str]] = defaultdict(list)

    for row in spec_rows:
        source_url = str(row.get("source_url", "")).strip()
        standard_field = str(row.get("standard_field", "")).strip()
        normalized_value = str(row.get("normalized_value", "") or "").strip()

        if not source_url or not standard_field or not normalized_value:
            continue

        if standard_field not in field_columns:
            field_columns.append(standard_field)

        key = (source_url, standard_field)
        candidate = {
            "normalized_value": normalized_value,
            "confidence": row.get("confidence", 0),
        }
        chosen = _choose_value(selected.get(key), candidate)

        if chosen is candidate and key in selected:
            previous_value = str(selected[key].get("normalized_value") or "")
            if previous_value and previous_value != normalized_value:
                extra_values[key].append(previous_value)
        elif chosen is not candidate:
            existing_value = str(selected[key].get("normalized_value") or "")
            if normalized_value and normalized_value != existing_value:
                extra_values[key].append(normalized_value)

        selected[key] = chosen

    matrix_rows: list[dict[str, Any]] = []
    for source_url in urls:
        row: dict[str, Any] = {"source_url": source_url}
        row.update(metadata.get(source_url, {"title": "", "brand": "", "model": ""}))

        for field in field_columns:
            key = (source_url, field)
            value = ""
            if key in selected:
                values = [str(selected[key].get("normalized_value") or "")]
                values.extend(extra_values.get(key, []))
                unique_values = [item for item in dict.fromkeys(values) if item]
                value = " | ".join(unique_values)
            row[field] = value

        matrix_rows.append(row)

    return pd.DataFrame(matrix_rows, columns=[*BASE_COLUMNS, *field_columns])

from __future__ import annotations

from typing import Any, Iterable

import pandas as pd

from src.specs.fields import get_spec_field, list_spec_fields

from .models import RequirementDraftRow


MATRIX_METADATA_COLUMNS = {
    "source_url",
    "title",
    "brand",
    "model",
}


def _records(value: pd.DataFrame | list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    if value is None:
        return []
    if isinstance(value, pd.DataFrame):
        return value.to_dict("records")
    return list(value or [])


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    if pd.isna(value):
        return True
    return str(value).strip() == ""


def _field_label(standard_field: str, language: str = "en") -> str:
    try:
        return get_spec_field(standard_field).label(language)
    except KeyError:
        return standard_field


def _known_spec_fields() -> set[str]:
    return {field.standard_field for field in list_spec_fields()}


def _field_order(
    specification_matrix: pd.DataFrame,
    fields: Iterable[str] | None = None,
) -> list[str]:
    if fields is not None:
        return list(dict.fromkeys(str(field) for field in fields if str(field).strip()))

    known_fields = _known_spec_fields()
    ordered: list[str] = []
    for column in specification_matrix.columns:
        column_name = str(column)
        if column_name in MATRIX_METADATA_COLUMNS:
            continue
        if column_name in known_fields:
            ordered.append(column_name)

    return ordered


def _gap_by_url(gap_analysis: pd.DataFrame | list[dict[str, Any]] | None) -> dict[str, dict[str, Any]]:
    gaps: dict[str, dict[str, Any]] = {}
    for row in _records(gap_analysis):
        source_url = str(row.get("source_url", "")).strip()
        if source_url:
            gaps[source_url] = row
    return gaps


def _action_for_value(current_value: str, risk_level: str, language: str = "en") -> str:
    if current_value:
        return "Keep as candidate requirement" if language == "en" else "保留为候选需求"

    if risk_level == "high":
        return "Required before product definition" if language == "en" else "产品定义前必须确认"
    if risk_level == "medium":
        return "Supplier follow-up required" if language == "en" else "需要向供应商追问"
    return "Optional follow-up" if language == "en" else "可选追问"


def build_requirement_draft(
    specification_matrix: pd.DataFrame,
    *,
    gap_analysis: pd.DataFrame | list[dict[str, Any]] | None = None,
    profile: str = "generic_hardware",
    fields: Iterable[str] | None = None,
    language: str = "en",
) -> pd.DataFrame:
    """Generate product requirement draft rows from a specification matrix.

    The draft preserves product metadata and translates matrix values into rows
    that can be reviewed by product developers or sent to engineering teams.
    """

    columns = [
        "source_url",
        "title",
        "brand",
        "model",
        "profile",
        "risk_level",
        "requirement_field",
        "requirement_label",
        "current_value",
        "evidence_source",
        "action",
        "notes",
    ]

    if specification_matrix is None or specification_matrix.empty:
        return pd.DataFrame(columns=columns)

    gap_lookup = _gap_by_url(gap_analysis)
    selected_fields = _field_order(specification_matrix, fields)

    rows: list[RequirementDraftRow] = []
    for _, product in specification_matrix.iterrows():
        source_url = str(product.get("source_url", "") or "").strip()
        risk_level = str(gap_lookup.get(source_url, {}).get("risk_level", "") or "").strip()
        if not risk_level:
            risk_level = "unknown"

        for field in selected_fields:
            value = product[field] if field in specification_matrix.columns else ""
            current_value = "" if _is_missing(value) else str(value).strip()
            evidence_source = "Specification Matrix" if current_value else "Gap Analysis"
            rows.append(
                RequirementDraftRow(
                    source_url=source_url,
                    title=str(product.get("title", "") or "").strip(),
                    brand=str(product.get("brand", "") or "").strip(),
                    model=str(product.get("model", "") or "").strip(),
                    profile=profile,
                    risk_level=risk_level,
                    requirement_field=field,
                    requirement_label=_field_label(field, language),
                    current_value=current_value,
                    evidence_source=evidence_source,
                    action=_action_for_value(current_value, risk_level, language),
                    notes="",
                )
            )

    return pd.DataFrame([row.as_dict() for row in rows], columns=columns)

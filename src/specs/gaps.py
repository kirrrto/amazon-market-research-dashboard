from __future__ import annotations

from typing import Any

import pandas as pd

from .fields import get_spec_field
from .profiles import SpecProfile, get_spec_profile


BASE_COLUMNS = ["source_url", "title", "brand", "model"]


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    if pd.isna(value):
        return True
    return str(value).strip() == ""


def risk_level_for_missing_count(missing_count: int) -> str:
    """Assign a simple risk level based on missing required specification count."""

    if missing_count <= 1:
        return "low"
    if missing_count <= 3:
        return "medium"
    return "high"


def _field_label(standard_field: str, language: str = "en") -> str:
    try:
        return get_spec_field(standard_field).label(language)
    except KeyError:
        return standard_field


def _profile(profile: str | SpecProfile) -> SpecProfile:
    if isinstance(profile, SpecProfile):
        return profile
    return get_spec_profile(str(profile))


def build_gap_analysis(
    specification_matrix: pd.DataFrame,
    *,
    profile: str | SpecProfile = "generic_hardware",
    language: str = "en",
) -> pd.DataFrame:
    """Generate required-field gap analysis for a specification matrix.

    Parameters
    ----------
    specification_matrix:
        Product-by-field matrix produced by ``build_specification_matrix``.
    profile:
        Required specification profile id or SpecProfile instance.
    language:
        Controls human-readable profile and field labels.

    Returns
    -------
    pandas.DataFrame
        One row per product, listing missing required fields and risk level.
    """

    selected_profile = _profile(profile)
    required_fields = list(selected_profile.required_fields)
    required_total = len(required_fields)

    rows: list[dict[str, Any]] = []
    if specification_matrix is None or specification_matrix.empty:
        return pd.DataFrame(
            columns=[
                "source_url",
                "title",
                "brand",
                "model",
                "profile",
                "profile_label",
                "missing_fields",
                "missing_labels",
                "missing_count",
                "required_fields_count",
                "completion_rate",
                "risk_level",
            ]
        )

    for _, matrix_row in specification_matrix.iterrows():
        missing_fields: list[str] = []
        missing_labels: list[str] = []

        for field in required_fields:
            value = matrix_row[field] if field in specification_matrix.columns else ""
            if _is_missing(value):
                missing_fields.append(field)
                missing_labels.append(_field_label(field, language))

        missing_count = len(missing_fields)
        completion_rate = (
            (required_total - missing_count) / required_total
            if required_total
            else 1.0
        )

        rows.append(
            {
                "source_url": str(matrix_row.get("source_url", "") or ""),
                "title": str(matrix_row.get("title", "") or ""),
                "brand": str(matrix_row.get("brand", "") or ""),
                "model": str(matrix_row.get("model", "") or ""),
                "profile": selected_profile.profile_id,
                "profile_label": selected_profile.label(language),
                "missing_fields": ", ".join(missing_fields),
                "missing_labels": ", ".join(missing_labels),
                "missing_count": missing_count,
                "required_fields_count": required_total,
                "completion_rate": round(completion_rate, 4),
                "risk_level": risk_level_for_missing_count(missing_count),
            }
        )

    return pd.DataFrame(
        rows,
        columns=[
            "source_url",
            "title",
            "brand",
            "model",
            "profile",
            "profile_label",
            "missing_fields",
            "missing_labels",
            "missing_count",
            "required_fields_count",
            "completion_rate",
            "risk_level",
        ],
    )

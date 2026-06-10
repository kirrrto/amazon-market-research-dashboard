from __future__ import annotations

from typing import Any

import pandas as pd

from src.analysis import NUMERIC_COLUMNS, clean_market_data_with_report

from .models import ImportIssue, ImportReport, ImportResult


def _is_blank(value: Any) -> bool:
    return pd.isna(value) or str(value).strip() == ""


def _parse_numeric(value: Any) -> float | None:
    if _is_blank(value):
        return None
    text = str(value).strip()
    for token in (",", "$", "£", "€", "¥", "%"):
        text = text.replace(token, "")
    extracted = pd.Series([text], dtype="string").str.extract(
        r"([-+]?(?:\d+(?:\.\d*)?|\.\d+))",
        expand=False,
    )
    number = pd.to_numeric(extracted, errors="coerce").iloc[0]
    return None if pd.isna(number) else float(number)


def validate_and_clean_import(
    mapped_frame: pd.DataFrame,
    *,
    source_file: str,
    worksheet: str | None,
    mapping: dict[str, str],
) -> ImportResult:
    issues: list[ImportIssue] = []
    error_rows: set[int] = set()
    warning_rows: set[int] = set()
    seen_asins: set[str] = set()

    for position, (_, row) in enumerate(mapped_frame.iterrows(), start=2):
        asin_raw = row.get("asin")
        asin = "" if _is_blank(asin_raw) else str(asin_raw).strip().upper()

        if not asin:
            error_rows.add(position)
            issues.append(
                ImportIssue(
                    position,
                    "error",
                    "asin",
                    "missing_asin",
                    asin_raw,
                    "ASIN is required; the row will be rejected.",
                )
            )
        elif asin in seen_asins:
            error_rows.add(position)
            issues.append(
                ImportIssue(
                    position,
                    "error",
                    "asin",
                    "duplicate_asin",
                    asin_raw,
                    "Duplicate ASIN; only the first row will be retained.",
                )
            )
        else:
            seen_asins.add(asin)

        for field in NUMERIC_COLUMNS:
            raw_value = row.get(field)
            parsed = _parse_numeric(raw_value)
            if parsed is None:
                error_rows.add(position)
                issues.append(
                    ImportIssue(
                        position,
                        "error",
                        field,
                        "invalid_numeric",
                        raw_value,
                        f"{field} could not be converted to a number.",
                    )
                )
                continue

            if field in {"price", "reviews", "monthly_sales"} and parsed < 0:
                warning_rows.add(position)
                issues.append(
                    ImportIssue(
                        position,
                        "warning",
                        field,
                        "negative_value_normalized",
                        raw_value,
                        f"Negative {field} will be normalized to zero.",
                    )
                )
            if field == "rating" and not 0 <= parsed <= 5:
                warning_rows.add(position)
                issues.append(
                    ImportIssue(
                        position,
                        "warning",
                        field,
                        "rating_out_of_range",
                        raw_value,
                        "Rating will be limited to the 0–5 range.",
                    )
                )

        for field, replacement in (
            ("brand", "Unknown"),
            ("category", "Uncategorized"),
        ):
            if _is_blank(row.get(field)):
                warning_rows.add(position)
                issues.append(
                    ImportIssue(
                        position,
                        "warning",
                        field,
                        "blank_value_normalized",
                        row.get(field),
                        f"Blank {field} will be replaced with '{replacement}'.",
                    )
                )

    try:
        products, cleaning_report = clean_market_data_with_report(mapped_frame)
    except ValueError:
        products = pd.DataFrame(
            columns=[
                *mapped_frame.columns,
                "estimated_monthly_revenue",
                "opportunity_score",
            ]
        )
        cleaning_report = None

    duplicate_count = sum(
        issue.error_code == "duplicate_asin" for issue in issues
    )
    report = ImportReport(
        source_file=source_file,
        worksheet=worksheet,
        original_rows=int(len(mapped_frame)),
        valid_rows=int(len(products)),
        rejected_rows=len(error_rows),
        warning_rows=len(warning_rows),
        duplicate_asins=int(duplicate_count),
        mapping=dict(mapping),
    )

    return ImportResult(products=products, issues=issues, report=report)

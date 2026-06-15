from __future__ import annotations

from io import BytesIO

import pandas as pd
from openpyxl.styles import Font, PatternFill

from src.i18n import column_label, normalize_language, sheet_label
from src.specs import normalize_raw_specifications

from .models import FetchResult


HEADER_FILL = PatternFill("solid", fgColor="1F4E78")
HEADER_FONT = Font(color="FFFFFF", bold=True)


def _style_sheet(worksheet) -> None:
    worksheet.freeze_panes = "A2"
    for cell in worksheet[1]:
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT

    for column_cells in worksheet.columns:
        letter = column_cells[0].column_letter
        values = [str(cell.value or "") for cell in column_cells[:100]]
        width = min(max(max(map(len, values), default=8) + 2, 10), 60)
        worksheet.column_dimensions[letter].width = width


def _localized_frame(frame: pd.DataFrame, language: str) -> pd.DataFrame:
    if frame.empty:
        return frame.rename(columns={column: column_label(str(column), language) for column in frame.columns})
    return frame.rename(columns={column: column_label(str(column), language) for column in frame.columns})


def normalized_specs_frame(result: FetchResult, language: str = "en") -> pd.DataFrame:
    """Build a normalized specification frame from raw connector specifications."""

    raw_frame = result.raw_specs_frame
    if raw_frame.empty:
        columns = [
            "source_url",
            "standard_field",
            "standard_label",
            "raw_spec_name",
            "raw_spec_value",
            "normalized_value",
            "confidence",
            "category",
            "parser",
            "fetched_at",
        ]
        return pd.DataFrame(columns=columns)

    rows = normalize_raw_specifications(
        raw_frame.to_dict("records"),
        language=language,
    )
    columns = [
        "source_url",
        "standard_field",
        "standard_label",
        "raw_spec_name",
        "raw_spec_value",
        "normalized_value",
        "confidence",
        "category",
        "parser",
        "fetched_at",
    ]
    if not rows:
        return pd.DataFrame(columns=columns)
    return pd.DataFrame(rows, columns=columns)


def build_product_page_workbook(result: FetchResult, language: str = "en") -> bytes:
    """Build a workbook for public product page connector results."""

    code = normalize_language(language)
    buffer = BytesIO()

    products = _localized_frame(result.products_frame, code)
    raw_specs = _localized_frame(result.raw_specs_frame, code)
    normalized_specs = _localized_frame(normalized_specs_frame(result, code), code)
    fetch_logs = _localized_frame(result.fetch_logs_frame, code)
    issues = _localized_frame(result.issues_frame, code)

    sheet_names = [
        sheet_label("products", code),
        sheet_label("raw_specifications", code),
        sheet_label("normalized_specifications", code),
        sheet_label("fetch_logs", code),
        sheet_label("issues", code),
    ]

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        products.to_excel(writer, sheet_name=sheet_names[0], index=False)
        raw_specs.to_excel(writer, sheet_name=sheet_names[1], index=False)
        normalized_specs.to_excel(writer, sheet_name=sheet_names[2], index=False)
        fetch_logs.to_excel(writer, sheet_name=sheet_names[3], index=False)
        issues.to_excel(writer, sheet_name=sheet_names[4], index=False)

        for sheet_name in sheet_names:
            _style_sheet(writer.book[sheet_name])

    buffer.seek(0)
    return buffer.getvalue()

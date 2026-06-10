from __future__ import annotations

from io import BytesIO
from typing import Iterable

import pandas as pd
from openpyxl.styles import Font, PatternFill

from .models import ImportResult


HEADER_FILL = PatternFill("solid", fgColor="1F4E78")
HEADER_FONT = Font(color="FFFFFF", bold=True)


def _style_sheet(worksheet, freeze_panes: str = "A2") -> None:
    worksheet.freeze_panes = freeze_panes
    for cell in worksheet[1]:
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT

    for column_cells in worksheet.columns:
        letter = column_cells[0].column_letter
        values = [str(cell.value or "") for cell in column_cells[:100]]
        width = min(max(max(map(len, values), default=8) + 2, 10), 40)
        worksheet.column_dimensions[letter].width = width


def build_normalized_workbook(result: ImportResult) -> bytes:
    buffer = BytesIO()
    issues = result.issues_frame

    summary = pd.DataFrame(
        result.report.summary_rows(),
        columns=["Item", "Value"],
    )
    mapping = pd.DataFrame(
        sorted(result.report.mapping.items()),
        columns=["Standard field", "Source column"],
    )

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        result.products.to_excel(writer, sheet_name="Products", index=False)
        issues.to_excel(writer, sheet_name="Issues", index=False)
        summary.to_excel(
            writer,
            sheet_name="Import Report",
            index=False,
            startrow=0,
        )
        mapping.to_excel(
            writer,
            sheet_name="Import Report",
            index=False,
            startrow=len(summary) + 3,
        )

        _style_sheet(writer.book["Products"])
        _style_sheet(writer.book["Issues"])
        report_sheet = writer.book["Import Report"]
        _style_sheet(report_sheet)
        mapping_header_row = len(summary) + 4
        for cell in report_sheet[mapping_header_row]:
            cell.fill = HEADER_FILL
            cell.font = HEADER_FONT

    buffer.seek(0)
    return buffer.getvalue()

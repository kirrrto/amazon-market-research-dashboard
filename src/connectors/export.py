from __future__ import annotations

from io import BytesIO

import pandas as pd
from openpyxl.styles import Font, PatternFill

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


def build_product_page_workbook(result: FetchResult) -> bytes:
    """Build a workbook for public product page connector results."""

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        result.products_frame.to_excel(writer, sheet_name="Products", index=False)
        result.raw_specs_frame.to_excel(
            writer,
            sheet_name="Raw Specifications",
            index=False,
        )
        result.fetch_logs_frame.to_excel(writer, sheet_name="Fetch Logs", index=False)
        result.issues_frame.to_excel(writer, sheet_name="Issues", index=False)

        for sheet_name in [
            "Products",
            "Raw Specifications",
            "Fetch Logs",
            "Issues",
        ]:
            _style_sheet(writer.book[sheet_name])

    buffer.seek(0)
    return buffer.getvalue()

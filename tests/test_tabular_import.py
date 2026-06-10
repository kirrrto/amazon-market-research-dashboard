from io import BytesIO

import pandas as pd
import pytest

from src.importers.tabular import (
    MAX_FILE_SIZE_BYTES,
    TabularImportError,
    _excel_engine,
    list_worksheets,
    read_tabular_file,
)


def xlsx_bytes() -> bytes:
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        pd.DataFrame({"ASIN": ["A1"], "Price": [10]}).to_excel(
            writer, sheet_name="Amazon US", index=False
        )
        pd.DataFrame({"型号": ["C1"], "价格": [20]}).to_excel(
            writer, sheet_name="供应商", index=False
        )
    return buffer.getvalue()


def test_reads_utf8_csv():
    result = read_tabular_file(
        "products.csv",
        "ASIN,价格\nA1,79.99\n".encode("utf-8"),
    )
    assert result.to_dict("records") == [{"ASIN": "A1", "价格": 79.99}]


def test_reads_gb18030_csv():
    content = "ASIN,品牌\nA1,示例品牌\n".encode("gb18030")
    result = read_tabular_file("products.csv", content)
    assert result.loc[0, "品牌"] == "示例品牌"


def test_lists_excel_worksheets():
    assert list_worksheets("products.xlsx", xlsx_bytes()) == [
        "Amazon US",
        "供应商",
    ]


def test_reads_selected_excel_worksheet():
    result = read_tabular_file(
        "products.xlsx",
        xlsx_bytes(),
        worksheet="供应商",
    )
    assert result.loc[0, "型号"] == "C1"


def test_missing_worksheet_has_clear_error():
    with pytest.raises(TabularImportError, match="does not exist"):
        read_tabular_file(
            "products.xlsx",
            xlsx_bytes(),
            worksheet="Missing",
        )


def test_rejects_unsupported_extension():
    with pytest.raises(TabularImportError, match="Unsupported file type"):
        read_tabular_file("products.json", b"{}")


def test_rejects_empty_file():
    with pytest.raises(TabularImportError, match="empty"):
        read_tabular_file("products.csv", b"")


def test_rejects_project_size_limit():
    with pytest.raises(TabularImportError, match="exceeds"):
        read_tabular_file(
            "products.csv",
            b"x" * (MAX_FILE_SIZE_BYTES + 1),
        )


def test_xls_uses_xlrd_engine():
    assert _excel_engine(".xls") == "xlrd"
    assert _excel_engine(".xlsx") == "openpyxl"

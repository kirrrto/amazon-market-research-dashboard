from io import BytesIO

import pandas as pd

from src.importers.export import build_normalized_workbook
from src.importers.validation import validate_and_clean_import


MAPPING = {
    "asin": "ASIN",
    "title": "Title",
    "brand": "Brand",
    "price": "Price",
    "rating": "Rating",
    "reviews": "Reviews",
    "monthly_sales": "Monthly Sales",
    "category": "Category",
}


def source_frame():
    return pd.DataFrame(
        [
            {
                "asin": "a1",
                "title": "Camera A",
                "brand": "",
                "price": "$79.99",
                "rating": 6,
                "reviews": -2,
                "monthly_sales": "1,000",
                "category": "",
            },
            {
                "asin": "A1",
                "title": "Duplicate",
                "brand": "Brand A",
                "price": 80,
                "rating": 4,
                "reviews": 20,
                "monthly_sales": 10,
                "category": "Camera",
            },
            {
                "asin": "A3",
                "title": "Invalid",
                "brand": "Brand B",
                "price": "Contact seller",
                "rating": 4,
                "reviews": 20,
                "monthly_sales": 10,
                "category": "Camera",
            },
        ]
    )


def test_validation_returns_products_and_row_level_issues():
    result = validate_and_clean_import(
        source_frame(),
        source_file="research.xlsx",
        worksheet="Amazon US",
        mapping=MAPPING,
    )

    assert len(result.products) == 1
    assert result.report.original_rows == 3
    assert result.report.valid_rows == 1
    assert result.report.rejected_rows == 2
    assert result.report.warning_rows == 1
    assert result.report.duplicate_asins == 1

    codes = {issue.error_code for issue in result.issues}
    assert "duplicate_asin" in codes
    assert "invalid_numeric" in codes
    assert "blank_value_normalized" in codes
    assert "rating_out_of_range" in codes


def test_invalid_rows_include_spreadsheet_row_numbers():
    result = validate_and_clean_import(
        source_frame(),
        source_file="research.xlsx",
        worksheet="Amazon US",
        mapping=MAPPING,
    )
    duplicate = next(
        issue for issue in result.issues
        if issue.error_code == "duplicate_asin"
    )
    assert duplicate.row_number == 3


def test_export_contains_required_worksheets():
    result = validate_and_clean_import(
        source_frame(),
        source_file="research.xlsx",
        worksheet="Amazon US",
        mapping=MAPPING,
    )
    workbook = build_normalized_workbook(result)
    excel = pd.ExcelFile(BytesIO(workbook), engine="openpyxl")
    assert excel.sheet_names == ["Products", "Issues", "Import Report"]


def test_export_preserves_mapping_and_summary():
    result = validate_and_clean_import(
        source_frame(),
        source_file="research.xlsx",
        worksheet="Amazon US",
        mapping=MAPPING,
    )
    workbook = build_normalized_workbook(result)
    report = pd.read_excel(
        BytesIO(workbook),
        sheet_name="Import Report",
        engine="openpyxl",
        header=None,
    )
    values = report.fillna("").astype(str).values.ravel().tolist()
    assert "Source file" in values
    assert "research.xlsx" in values
    assert "Standard field" in values
    assert "ASIN" in values

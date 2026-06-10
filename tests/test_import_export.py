from io import BytesIO

import pandas as pd

from src.finance import ProfitAssumptions
from src.importers.export import (
    build_normalized_workbook,
    prepare_export_result,
)
from src.importers.models import ImportIssue, ImportReport, ImportResult
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



def test_issue_frame_displays_missing_values_as_blank():
    report = ImportReport(
        source_file="research.xlsx",
        worksheet="Amazon US",
        original_rows=1,
        valid_rows=1,
        rejected_rows=0,
        warning_rows=1,
        duplicate_asins=0,
        mapping=MAPPING,
    )
    result = ImportResult(
        products=pd.DataFrame(),
        issues=[
            ImportIssue(
                row_number=2,
                severity="warning",
                field="brand",
                error_code="blank_value_normalized",
                raw_value=float("nan"),
                message="Blank brand will be replaced with 'Unknown'.",
            )
        ],
        report=report,
    )

    assert result.issues_frame.loc[0, "raw_value"] == "(blank)"


def test_prepare_export_result_includes_profit_columns():
    result = validate_and_clean_import(
        source_frame(),
        source_file="research.xlsx",
        worksheet="Amazon US",
        mapping=MAPPING,
    )
    assumptions = ProfitAssumptions(
        product_cost=30,
        shipping_cost=8,
        platform_fee_rate=0.15,
        advertising_cost_rate=0.10,
        return_rate=0.05,
    )
    export_result = prepare_export_result(result, assumptions)

    expected_columns = {
        "estimated_unit_gross_profit",
        "estimated_unit_net_profit",
        "estimated_net_margin",
        "break_even_price",
        "estimated_monthly_net_profit",
    }
    assert expected_columns.issubset(export_result.products.columns)


def test_exported_profit_values_use_current_assumptions():
    result = validate_and_clean_import(
        source_frame(),
        source_file="research.xlsx",
        worksheet="Amazon US",
        mapping=MAPPING,
    )
    low_cost = ProfitAssumptions(
        product_cost=10,
        shipping_cost=2,
        platform_fee_rate=0.15,
        advertising_cost_rate=0.10,
        return_rate=0.05,
    )
    high_cost = ProfitAssumptions(
        product_cost=50,
        shipping_cost=15,
        platform_fee_rate=0.15,
        advertising_cost_rate=0.10,
        return_rate=0.05,
    )

    low_result = prepare_export_result(result, low_cost)
    high_result = prepare_export_result(result, high_cost)

    assert (
        low_result.products["estimated_unit_net_profit"].iloc[0]
        > high_result.products["estimated_unit_net_profit"].iloc[0]
    )


def test_workbook_products_sheet_contains_profit_columns():
    result = validate_and_clean_import(
        source_frame(),
        source_file="research.xlsx",
        worksheet="Amazon US",
        mapping=MAPPING,
    )
    assumptions = ProfitAssumptions(
        product_cost=30,
        shipping_cost=8,
        platform_fee_rate=0.15,
        advertising_cost_rate=0.10,
        return_rate=0.05,
    )
    workbook = build_normalized_workbook(
        prepare_export_result(result, assumptions)
    )
    products = pd.read_excel(
        BytesIO(workbook),
        sheet_name="Products",
        engine="openpyxl",
    )
    assert "estimated_monthly_net_profit" in products.columns

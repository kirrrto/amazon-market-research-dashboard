from io import BytesIO

import pandas as pd

from src.finance import ProfitAssumptions
from src.importers.export import build_normalized_workbook, prepare_export_result
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
                "asin": "A1",
                "title": "Camera",
                "brand": "Brand",
                "price": 100,
                "rating": 4.5,
                "reviews": 100,
                "monthly_sales": 50,
                "category": "Security Camera",
            }
        ]
    )


def test_normalized_workbook_defaults_to_english_sheets():
    result = validate_and_clean_import(
        source_frame(),
        source_file="research.xlsx",
        worksheet="Amazon US",
        mapping=MAPPING,
    )
    export_result = prepare_export_result(
        result,
        ProfitAssumptions(
            product_cost=20,
            shipping_cost=5,
            platform_fee_rate=0.15,
            advertising_cost_rate=0.10,
            return_rate=0.05,
        ),
    )
    workbook = build_normalized_workbook(export_result)
    excel = pd.ExcelFile(BytesIO(workbook), engine="openpyxl")
    assert excel.sheet_names == ["Products", "Issues", "Import Report"]


def test_normalized_workbook_supports_chinese_sheets_and_columns():
    result = validate_and_clean_import(
        source_frame(),
        source_file="research.xlsx",
        worksheet="Amazon US",
        mapping=MAPPING,
    )
    export_result = prepare_export_result(
        result,
        ProfitAssumptions(
            product_cost=20,
            shipping_cost=5,
            platform_fee_rate=0.15,
            advertising_cost_rate=0.10,
            return_rate=0.05,
        ),
    )
    workbook = build_normalized_workbook(export_result, language="zh-CN")
    excel = pd.ExcelFile(BytesIO(workbook), engine="openpyxl")

    assert excel.sheet_names == ["产品数据", "问题记录", "导入报告"]

    products = pd.read_excel(BytesIO(workbook), sheet_name="产品数据", engine="openpyxl")
    assert "标题" in products.columns
    assert "预估月净利润" in products.columns

    report = pd.read_excel(BytesIO(workbook), sheet_name="导入报告", engine="openpyxl", header=None)
    values = report.fillna("").astype(str).values.ravel().tolist()
    assert "项目" in values
    assert "标准字段" in values

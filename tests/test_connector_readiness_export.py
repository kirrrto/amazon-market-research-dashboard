from io import BytesIO

import pandas as pd

from src.connectors.export import (
    build_product_page_workbook,
    product_pool_summary_frame,
    product_readiness_summary_frame,
    supplier_comparison_frame,
)
from src.connectors.models import FetchLog, FetchResult, ProductPageRecord


def sample_result() -> FetchResult:
    record_a = ProductPageRecord(
        source_url="https://supplier-a.example.com/camera-a",
        status="parsed",
        status_code=200,
        title="Vehicle Camera A",
        brand="Supplier A",
        model="A1",
        raw_specs=[
            {"name": "Power Supply", "value": "DC：10-32V", "parser": "html.table"},
            {"name": "Operating Temperature", "value": "-20℃～70℃", "parser": "html.table"},
            {"name": "Waterproof Rating", "value": "IP69K", "parser": "html.table"},
        ],
    )
    record_b = ProductPageRecord(
        source_url="https://supplier-b.example.com/camera-b",
        status="parsed",
        status_code=200,
        title="Vehicle Camera B",
        brand="Supplier B",
        model="B1",
        raw_specs=[
            {"name": "Power Supply", "value": "DC 12V", "parser": "html.table"},
        ],
    )
    return FetchResult(
        records=[record_a, record_b],
        fetch_logs=[
            FetchLog(
                source_url=record_a.source_url,
                domain=record_a.domain,
                success=True,
                status_code=200,
                elapsed_ms=10,
            ),
            FetchLog(
                source_url=record_b.source_url,
                domain=record_b.domain,
                success=True,
                status_code=200,
                elapsed_ms=12,
            ),
        ],
        issues=[],
    )


def test_product_readiness_summary_frame_contains_scores():
    frame = product_readiness_summary_frame(
        sample_result(),
        profile="vehicle_camera",
        language="en",
    )

    assert "readiness_score" in frame.columns
    assert "readiness_status" in frame.columns
    assert "recommendation" in frame.columns
    assert len(frame) == 2
    assert frame["readiness_score"].max() <= 100


def test_supplier_comparison_frame_aggregates_products():
    frame = supplier_comparison_frame(
        sample_result(),
        profile="vehicle_camera",
        language="en",
    )

    assert "supplier_name" in frame.columns
    assert "average_readiness_score" in frame.columns
    assert "overall_status" in frame.columns
    assert set(frame["supplier_name"]) == {"Supplier A", "Supplier B"}


def test_product_pool_summary_frame_contains_priority_and_supplier_context():
    frame = product_pool_summary_frame(
        sample_result(),
        profile="vehicle_camera",
        language="en",
    )

    assert "product_pool_status" in frame.columns
    assert "priority" in frame.columns
    assert "supplier_average_readiness_score" in frame.columns
    assert len(frame) == 2


def test_product_page_workbook_exports_readiness_and_supplier_sheets():
    workbook = build_product_page_workbook(
        sample_result(),
        language="en",
        profile="vehicle_camera",
    )
    excel = pd.ExcelFile(BytesIO(workbook), engine="openpyxl")

    assert excel.sheet_names == [
        "Products",
        "Raw Specifications",
        "Normalized Specifications",
        "Specification Matrix",
        "Coverage Summary",
        "Gap Analysis",
        "Product Requirement Draft",
        "Supplier Follow-up Questions",
        "Decision Summary",
        "Product Readiness Summary",
        "Supplier Comparison",
        "Product Pool Summary",
        "Fetch Logs",
        "Issues",
    ]

    readiness = pd.read_excel(
        BytesIO(workbook),
        sheet_name="Product Readiness Summary",
        engine="openpyxl",
    )
    suppliers = pd.read_excel(
        BytesIO(workbook),
        sheet_name="Supplier Comparison",
        engine="openpyxl",
    )
    product_pool = pd.read_excel(
        BytesIO(workbook),
        sheet_name="Product Pool Summary",
        engine="openpyxl",
    )

    assert "readiness_score" in readiness.columns
    assert "supplier_name" in suppliers.columns
    assert "product_pool_status" in product_pool.columns


def test_product_page_workbook_exports_chinese_readiness_and_supplier_sheets():
    workbook = build_product_page_workbook(
        sample_result(),
        language="zh-CN",
        profile="vehicle_camera",
    )
    excel = pd.ExcelFile(BytesIO(workbook), engine="openpyxl")

    assert "产品就绪度汇总" in excel.sheet_names
    assert "供应商对比" in excel.sheet_names
    assert "产品池汇总" in excel.sheet_names

    readiness = pd.read_excel(
        BytesIO(workbook),
        sheet_name="产品就绪度汇总",
        engine="openpyxl",
    )
    suppliers = pd.read_excel(
        BytesIO(workbook),
        sheet_name="供应商对比",
        engine="openpyxl",
    )
    product_pool = pd.read_excel(
        BytesIO(workbook),
        sheet_name="产品池汇总",
        engine="openpyxl",
    )

    assert "就绪度评分" in readiness.columns
    assert "供应商名称" in suppliers.columns
    assert "产品池状态" in product_pool.columns

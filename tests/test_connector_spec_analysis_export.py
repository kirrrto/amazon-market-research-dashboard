from io import BytesIO

import pandas as pd

from src.connectors.export import (
    build_product_page_workbook,
    coverage_summary_frame,
    gap_analysis_frame,
    specification_matrix_frame,
)
from src.connectors.models import FetchLog, FetchResult, ProductPageRecord


def sample_result() -> FetchResult:
    record_a = ProductPageRecord(
        source_url="https://supplier.example.com/a",
        status="parsed",
        status_code=200,
        title="Vehicle Camera A",
        brand="Brand A",
        model="A1",
        raw_specs=[
            {"name": "Power Supply", "value": "DC：10-32V", "parser": "html.table"},
            {"name": "Operating Temperature", "value": "-20℃～70℃", "parser": "html.table"},
        ],
    )
    record_b = ProductPageRecord(
        source_url="https://supplier.example.com/b",
        status="parsed",
        status_code=200,
        title="Vehicle Camera B",
        brand="Brand B",
        model="B1",
        raw_specs=[
            {"name": "Power Supply", "value": "DC 12V", "parser": "html.table"},
            {"name": "Waterproof Rating", "value": "IP69K", "parser": "html.table"},
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


def test_specification_matrix_frame_contains_product_by_field_values():
    matrix = specification_matrix_frame(sample_result())

    assert len(matrix) == 2
    assert "power_input" in matrix.columns
    assert "operating_temperature" in matrix.columns

    first = matrix[matrix["source_url"] == "https://supplier.example.com/a"].iloc[0]
    assert first["title"] == "Vehicle Camera A"
    assert first["power_input"] == "DC 10-32V"
    assert first["operating_temperature"] == "-20°C to 70°C"


def test_coverage_summary_frame_counts_product_coverage():
    coverage = coverage_summary_frame(sample_result())

    power = coverage[coverage["standard_field"] == "power_input"].iloc[0]
    assert power["products_with_value"] == 2
    assert power["total_products"] == 2
    assert power["coverage_rate"] == 1.0

    operating = coverage[coverage["standard_field"] == "operating_temperature"].iloc[0]
    assert operating["products_with_value"] == 1
    assert operating["coverage_rate"] == 0.5


def test_gap_analysis_frame_uses_selected_profile():
    gaps = gap_analysis_frame(sample_result(), profile="vehicle_camera")

    assert len(gaps) == 2
    assert set(gaps["profile"]) == {"vehicle_camera"}
    assert "latency_ms" in gaps.loc[0, "missing_fields"]


def test_product_page_workbook_exports_spec_analysis_sheets():
    workbook = build_product_page_workbook(sample_result(), language="en", profile="vehicle_camera")
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

    matrix = pd.read_excel(BytesIO(workbook), sheet_name="Specification Matrix", engine="openpyxl")
    coverage = pd.read_excel(BytesIO(workbook), sheet_name="Coverage Summary", engine="openpyxl")
    gaps = pd.read_excel(BytesIO(workbook), sheet_name="Gap Analysis", engine="openpyxl")

    assert "power_input" in matrix.columns
    assert "coverage_rate" in coverage.columns
    assert "missing_fields" in gaps.columns


def test_product_page_workbook_exports_chinese_spec_analysis_sheets():
    workbook = build_product_page_workbook(sample_result(), language="zh-CN", profile="vehicle_camera")
    excel = pd.ExcelFile(BytesIO(workbook), engine="openpyxl")

    assert excel.sheet_names == [
        "产品数据",
        "原始规格",
        "标准化规格",
        "规格矩阵",
        "覆盖率汇总",
        "缺口分析",
        "产品需求草案",
        "供应商追问清单",
        "决策摘要",
        "产品就绪度汇总",
        "供应商对比",
        "产品池汇总",
        "抓取日志",
        "问题记录",
    ]

    matrix = pd.read_excel(BytesIO(workbook), sheet_name="规格矩阵", engine="openpyxl")
    coverage = pd.read_excel(BytesIO(workbook), sheet_name="覆盖率汇总", engine="openpyxl")
    gaps = pd.read_excel(BytesIO(workbook), sheet_name="缺口分析", engine="openpyxl")

    assert "供电输入" in matrix.columns
    assert "覆盖率" in coverage.columns
    assert "缺失字段" in gaps.columns

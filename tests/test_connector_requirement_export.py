from io import BytesIO

import pandas as pd

from src.connectors.export import (
    build_product_page_workbook,
    decision_summary_frame,
    requirement_draft_frame,
    supplier_follow_up_frame,
)
from src.connectors.models import FetchLog, FetchResult, ProductPageRecord


def sample_result() -> FetchResult:
    record = ProductPageRecord(
        source_url="https://supplier.example.com/vehicle-camera",
        status="parsed",
        status_code=200,
        title="Vehicle Camera",
        brand="Brand A",
        model="A1",
        raw_specs=[
            {"name": "Power Supply", "value": "DC：10-32V", "parser": "html.table"},
            {"name": "Operating Temperature", "value": "-20℃～70℃", "parser": "html.table"},
        ],
    )
    return FetchResult(
        records=[record],
        fetch_logs=[
            FetchLog(
                source_url=record.source_url,
                domain=record.domain,
                success=True,
                status_code=200,
                elapsed_ms=22,
            )
        ],
        issues=[],
    )


def test_requirement_draft_frame_uses_gap_risk():
    frame = requirement_draft_frame(
        sample_result(),
        profile="vehicle_camera",
        language="en",
    )

    assert "requirement_field" in frame.columns
    assert "risk_level" in frame.columns
    assert "power_input" in set(frame["requirement_field"])
    assert "Keep as candidate requirement" in set(frame["action"])


def test_supplier_follow_up_frame_generates_missing_field_questions():
    frame = supplier_follow_up_frame(
        sample_result(),
        profile="vehicle_camera",
        language="en",
    )

    assert "missing_field" in frame.columns
    assert "question" in frame.columns
    assert "waterproof_rating" in set(frame["missing_field"])
    assert any("waterproof" in question.lower() for question in frame["question"])


def test_decision_summary_frame_contains_recommendation():
    frame = decision_summary_frame(
        sample_result(),
        profile="vehicle_camera",
        language="en",
    )

    assert "recommendation" in frame.columns
    assert "next_action" in frame.columns
    assert frame.loc[0, "risk_level"] in {"medium", "high"}


def test_product_page_workbook_exports_requirement_sheets():
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

    draft = pd.read_excel(
        BytesIO(workbook),
        sheet_name="Product Requirement Draft",
        engine="openpyxl",
    )
    questions = pd.read_excel(
        BytesIO(workbook),
        sheet_name="Supplier Follow-up Questions",
        engine="openpyxl",
    )
    summary = pd.read_excel(
        BytesIO(workbook),
        sheet_name="Decision Summary",
        engine="openpyxl",
    )

    assert "requirement_field" in draft.columns
    assert "question" in questions.columns
    assert "recommendation" in summary.columns


def test_product_page_workbook_exports_chinese_requirement_sheets():
    workbook = build_product_page_workbook(
        sample_result(),
        language="zh-CN",
        profile="vehicle_camera",
    )
    excel = pd.ExcelFile(BytesIO(workbook), engine="openpyxl")

    assert "产品需求草案" in excel.sheet_names
    assert "供应商追问清单" in excel.sheet_names
    assert "决策摘要" in excel.sheet_names

    draft = pd.read_excel(
        BytesIO(workbook),
        sheet_name="产品需求草案",
        engine="openpyxl",
    )
    questions = pd.read_excel(
        BytesIO(workbook),
        sheet_name="供应商追问清单",
        engine="openpyxl",
    )
    summary = pd.read_excel(
        BytesIO(workbook),
        sheet_name="决策摘要",
        engine="openpyxl",
    )

    assert "需求字段" in draft.columns
    assert "追问问题" in questions.columns
    assert "建议" in summary.columns

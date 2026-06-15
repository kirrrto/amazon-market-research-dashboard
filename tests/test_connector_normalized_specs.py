from io import BytesIO

import pandas as pd

from src.connectors.export import build_product_page_workbook, normalized_specs_frame
from src.connectors.models import FetchLog, FetchResult, ProductPageRecord


def sample_result() -> FetchResult:
    record = ProductPageRecord(
        source_url="https://supplier.example.com/vehicle-camera",
        status="parsed",
        status_code=200,
        title="Vehicle Camera",
        raw_specs=[
            {"name": "Power Supply", "value": "DC：10-32V", "parser": "html.table"},
            {"name": "Operating Temperature", "value": "-20℃～70℃", "parser": "html.table"},
            {"name": "Marketing Feature", "value": "Easy installation", "parser": "html.table"},
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


def test_normalized_specs_frame_maps_common_fields():
    frame = normalized_specs_frame(sample_result(), language="en")

    assert set(frame["standard_field"]) == {"power_input", "operating_temperature"}
    power = frame[frame["standard_field"] == "power_input"].iloc[0]
    assert power["raw_spec_name"] == "Power Supply"
    assert power["normalized_value"] == "DC 10-32V"
    assert power["confidence"] == 1.0


def test_normalized_specs_frame_uses_chinese_labels():
    frame = normalized_specs_frame(sample_result(), language="zh-CN")
    assert "供电输入" in set(frame["standard_label"])
    assert "工作温度" in set(frame["standard_label"])


def test_product_page_workbook_exports_normalized_specs_sheet():
    workbook = build_product_page_workbook(sample_result(), language="en")
    excel = pd.ExcelFile(BytesIO(workbook), engine="openpyxl")

    assert "Normalized Specifications" in excel.sheet_names
    normalized = pd.read_excel(
        BytesIO(workbook),
        sheet_name="Normalized Specifications",
        engine="openpyxl",
    )
    assert "standard_field" in normalized.columns
    assert "power_input" in set(normalized["standard_field"])


def test_product_page_workbook_exports_chinese_sheet_and_column_labels():
    workbook = build_product_page_workbook(sample_result(), language="zh-CN")
    excel = pd.ExcelFile(BytesIO(workbook), engine="openpyxl")

    assert "标准化规格" in excel.sheet_names
    normalized = pd.read_excel(
        BytesIO(workbook),
        sheet_name="标准化规格",
        engine="openpyxl",
    )
    assert "标准字段" in normalized.columns
    assert "标准标签" in normalized.columns
    assert "供电输入" in set(normalized["标准标签"])

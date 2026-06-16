import pandas as pd

from src.specs import build_coverage_summary


def normalized_rows():
    return [
        {
            "source_url": "https://supplier.example.com/a",
            "standard_field": "power_input",
            "normalized_value": "DC 10-32V",
        },
        {
            "source_url": "https://supplier.example.com/a",
            "standard_field": "operating_temperature",
            "normalized_value": "-20°C to 70°C",
        },
        {
            "source_url": "https://supplier.example.com/b",
            "standard_field": "power_input",
            "normalized_value": "DC 12V",
        },
        {
            "source_url": "https://supplier.example.com/b",
            "standard_field": "waterproof_rating",
            "normalized_value": "",
        },
    ]


def product_rows():
    return [
        {"source_url": "https://supplier.example.com/a", "title": "Product A"},
        {"source_url": "https://supplier.example.com/b", "title": "Product B"},
        {"source_url": "https://supplier.example.com/c", "title": "Product C"},
    ]


def test_coverage_summary_uses_products_as_denominator():
    summary = build_coverage_summary(
        normalized_rows(),
        products=product_rows(),
        fields=["power_input", "operating_temperature", "waterproof_rating"],
    )

    power = summary[summary["standard_field"] == "power_input"].iloc[0]
    assert power["products_with_value"] == 2
    assert power["total_products"] == 3
    assert power["coverage_rate"] == 0.6667

    waterproof = summary[summary["standard_field"] == "waterproof_rating"].iloc[0]
    assert waterproof["products_with_value"] == 0
    assert waterproof["coverage_rate"] == 0.0


def test_coverage_summary_uses_specs_as_denominator_when_products_missing():
    summary = build_coverage_summary(
        normalized_rows(),
        fields=["power_input", "operating_temperature"],
    )

    power = summary[summary["standard_field"] == "power_input"].iloc[0]
    assert power["total_products"] == 2
    assert power["coverage_rate"] == 1.0


def test_coverage_summary_accepts_dataframes():
    summary = build_coverage_summary(
        pd.DataFrame(normalized_rows()),
        products=pd.DataFrame(product_rows()),
        fields=["power_input"],
    )

    assert summary.loc[0, "standard_field"] == "power_input"
    assert summary.loc[0, "products_with_value"] == 2


def test_coverage_summary_supports_chinese_labels():
    summary = build_coverage_summary(
        normalized_rows(),
        products=product_rows(),
        fields=["power_input"],
        language="zh-CN",
    )

    assert summary.loc[0, "standard_label"] == "供电输入"


def test_coverage_summary_includes_unknown_custom_fields():
    summary = build_coverage_summary(
        [
            {
                "source_url": "https://supplier.example.com/a",
                "standard_field": "custom_field",
                "normalized_value": "Custom value",
            }
        ],
        fields=["custom_field"],
    )

    assert summary.loc[0, "standard_label"] == "custom_field"
    assert summary.loc[0, "category"] == "custom"
    assert summary.loc[0, "coverage_rate"] == 1.0


def test_coverage_summary_handles_empty_input():
    summary = build_coverage_summary([], fields=["power_input"])
    assert summary.loc[0, "products_with_value"] == 0
    assert summary.loc[0, "total_products"] == 0
    assert summary.loc[0, "coverage_rate"] == 0.0

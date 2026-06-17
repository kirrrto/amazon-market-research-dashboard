import pandas as pd

from src.requirements import build_decision_summary, recommendation_for_risk


def gaps():
    return pd.DataFrame(
        [
            {
                "source_url": "https://supplier.example.com/a",
                "title": "Product A",
                "brand": "Brand A",
                "model": "A1",
                "profile": "vehicle_camera",
                "profile_label": "Vehicle Imaging",
                "risk_level": "low",
                "missing_count": 1,
                "required_fields_count": 8,
                "completion_rate": 0.875,
                "missing_fields": "latency_ms",
                "missing_labels": "Latency",
            },
            {
                "source_url": "https://supplier.example.com/b",
                "title": "Product B",
                "brand": "Brand B",
                "model": "B1",
                "profile": "vehicle_camera",
                "profile_label": "Vehicle Imaging",
                "risk_level": "medium",
                "missing_count": 3,
                "required_fields_count": 8,
                "completion_rate": 0.625,
                "missing_fields": "power_input, waterproof_rating, latency_ms",
                "missing_labels": "Power Input, Waterproof Rating, Latency",
            },
            {
                "source_url": "https://supplier.example.com/c",
                "title": "Product C",
                "brand": "Brand C",
                "model": "C1",
                "profile": "vehicle_camera",
                "profile_label": "Vehicle Imaging",
                "risk_level": "high",
                "missing_count": 5,
                "required_fields_count": 8,
                "completion_rate": 0.375,
                "missing_fields": "power_input, waterproof_rating, latency_ms, monitor_size, wireless_protocol",
                "missing_labels": "Power Input, Waterproof Rating, Latency, Monitor Size, Wireless Protocol",
            },
        ]
    )


def test_recommendation_for_risk_english():
    assert recommendation_for_risk("low", "en") == "Ready for product review"
    assert recommendation_for_risk("medium", "en") == "Supplier follow-up required before product definition"
    assert recommendation_for_risk("high", "en") == "Not ready for product definition"
    assert recommendation_for_risk("unexpected", "en") == "Review required"


def test_recommendation_for_risk_chinese():
    assert recommendation_for_risk("low", "zh-CN") == "可以进入产品评审"
    assert recommendation_for_risk("medium", "zh-CN") == "产品定义前需要供应商补充确认"
    assert recommendation_for_risk("high", "zh-CN") == "暂不适合进入产品定义"


def test_build_decision_summary_generates_one_row_per_product():
    summary = build_decision_summary(gaps(), language="en")

    assert len(summary) == 3
    assert list(summary["risk_level"]) == ["low", "medium", "high"]
    assert "recommendation" in summary.columns
    assert "next_action" in summary.columns


def test_decision_summary_preserves_gap_metrics():
    summary = build_decision_summary(gaps(), language="en")
    medium = summary[summary["risk_level"] == "medium"].iloc[0]

    assert medium["source_url"] == "https://supplier.example.com/b"
    assert medium["missing_count"] == 3
    assert medium["required_fields_count"] == 8
    assert medium["completion_rate"] == 0.625
    assert "power_input" in medium["missing_fields"]


def test_decision_summary_uses_chinese_recommendations_and_status():
    summary = build_decision_summary(gaps(), language="zh-CN")

    assert "可以进入产品评审" in set(summary["recommendation"])
    assert "暂不适合进入产品定义" in set(summary["recommendation"])
    assert set(summary["decision_status"]) == {"待处理"}


def test_decision_summary_handles_empty_input():
    summary = build_decision_summary([], language="en")
    assert summary.empty
    assert list(summary.columns) == [
        "source_url",
        "title",
        "brand",
        "model",
        "profile",
        "profile_label",
        "risk_level",
        "missing_count",
        "required_fields_count",
        "completion_rate",
        "recommendation",
        "next_action",
        "missing_fields",
        "missing_labels",
        "decision_owner",
        "decision_status",
        "notes",
    ]

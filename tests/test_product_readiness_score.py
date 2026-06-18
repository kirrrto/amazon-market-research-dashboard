import pandas as pd

from src.scoring import (
    build_product_readiness_summary,
    calculate_readiness_score,
    metadata_completeness,
    readiness_status_for_score,
)


def gap_rows():
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
                "missing_fields": "waterproof_rating, latency_ms, wireless_protocol",
                "missing_labels": "Waterproof Rating, Latency, Wireless Protocol",
            },
            {
                "source_url": "https://supplier.example.com/c",
                "title": "Product C",
                "brand": "",
                "model": "",
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


def supplier_questions():
    return pd.DataFrame(
        [
            {"source_url": "https://supplier.example.com/b", "missing_field": "waterproof_rating"},
            {"source_url": "https://supplier.example.com/b", "missing_field": "latency_ms"},
            {"source_url": "https://supplier.example.com/c", "missing_field": "power_input"},
            {"source_url": "https://supplier.example.com/c", "missing_field": "waterproof_rating"},
            {"source_url": "https://supplier.example.com/c", "missing_field": "latency_ms"},
        ]
    )


def requirement_draft():
    return pd.DataFrame(
        [
            {"source_url": "https://supplier.example.com/a", "current_value": "DC 10-32V"},
            {"source_url": "https://supplier.example.com/a", "current_value": "IP69K"},
            {"source_url": "https://supplier.example.com/b", "current_value": "DC 10-32V"},
            {"source_url": "https://supplier.example.com/b", "current_value": ""},
        ]
    )


def test_calculate_readiness_score_prioritizes_complete_low_risk_products():
    ready = calculate_readiness_score(
        completion_rate=0.875,
        risk_level="low",
        metadata_score=1.0,
        follow_up_question_count=0,
        requirement_candidate_count=2,
    )
    high_risk = calculate_readiness_score(
        completion_rate=0.375,
        risk_level="high",
        metadata_score=0.5,
        follow_up_question_count=3,
        requirement_candidate_count=0,
    )

    assert ready > 90
    assert high_risk < 40


def test_readiness_status_for_score_uses_score_and_risk_level():
    assert readiness_status_for_score(90, "low", "en") == "Ready for Review"
    assert readiness_status_for_score(70, "medium", "en") == "Follow-up Required"
    assert readiness_status_for_score(70, "high", "en") == "High Risk"
    assert readiness_status_for_score(30, "medium", "en") == "Not Ready"


def test_metadata_completeness_scores_product_identity_fields():
    assert metadata_completeness(
        {"source_url": "u", "title": "t", "brand": "b", "model": "m"}
    ) == 1.0
    assert metadata_completeness(
        {"source_url": "u", "title": "t", "brand": "", "model": ""}
    ) == 0.5


def test_build_product_readiness_summary_generates_sorted_rows():
    summary = build_product_readiness_summary(
        gap_rows(),
        supplier_follow_up=supplier_questions(),
        requirement_draft=requirement_draft(),
    )

    assert list(summary["source_url"])[0] == "https://supplier.example.com/a"
    assert summary.loc[0, "readiness_status"] == "Ready for Review"
    assert summary.loc[0, "readiness_score"] > summary.loc[1, "readiness_score"]
    assert set(summary["risk_level"]) == {"low", "medium", "high"}


def test_build_product_readiness_summary_counts_follow_up_and_requirement_candidates():
    summary = build_product_readiness_summary(
        gap_rows(),
        supplier_follow_up=supplier_questions(),
        requirement_draft=requirement_draft(),
    )

    product_b = summary[summary["source_url"] == "https://supplier.example.com/b"].iloc[0]
    assert product_b["follow_up_question_count"] == 2
    assert product_b["requirement_candidate_count"] == 1


def test_build_product_readiness_summary_supports_chinese_labels():
    summary = build_product_readiness_summary(gap_rows(), language="zh-CN")

    assert "可以进入评审" in set(summary["readiness_status"])
    assert "高风险" in set(summary["readiness_status"]) or "暂不建议继续" in set(summary["readiness_status"])
    assert summary.loc[0, "recommendation"]


def test_build_product_readiness_summary_computes_completion_rate_when_missing():
    rows = [
        {
            "source_url": "https://supplier.example.com/a",
            "title": "Product A",
            "brand": "Brand A",
            "model": "A1",
            "risk_level": "medium",
            "missing_count": 2,
            "required_fields_count": 10,
        }
    ]
    summary = build_product_readiness_summary(rows)

    assert summary.loc[0, "completion_rate"] == 0.8
    assert summary.loc[0, "readiness_score"] > 0


def test_build_product_readiness_summary_handles_empty_input():
    summary = build_product_readiness_summary([])

    assert summary.empty
    assert list(summary.columns) == [
        "source_url",
        "title",
        "brand",
        "model",
        "profile",
        "profile_label",
        "readiness_score",
        "readiness_status",
        "risk_level",
        "missing_count",
        "required_fields_count",
        "completion_rate",
        "metadata_completeness",
        "follow_up_question_count",
        "requirement_candidate_count",
        "recommendation",
        "next_action",
        "missing_fields",
        "missing_labels",
    ]

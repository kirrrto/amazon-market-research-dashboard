import pandas as pd

from src.suppliers import (
    build_supplier_comparison,
    supplier_group_key,
    supplier_status_for_score,
)


def readiness_rows():
    return pd.DataFrame(
        [
            {
                "source_url": "https://supplier-a.example.com/camera-a",
                "title": "Camera A",
                "brand": "Supplier A",
                "model": "A1",
                "readiness_score": 91.5,
                "readiness_status": "Ready for Review",
                "risk_level": "low",
                "missing_count": 1,
                "completion_rate": 0.9,
            },
            {
                "source_url": "https://supplier-a.example.com/camera-b",
                "title": "Camera B",
                "brand": "Supplier A",
                "model": "A2",
                "readiness_score": 73.0,
                "readiness_status": "Follow-up Required",
                "risk_level": "medium",
                "missing_count": 3,
                "completion_rate": 0.7,
            },
            {
                "source_url": "https://supplier-b.example.com/camera-c",
                "title": "Camera C",
                "brand": "Supplier B",
                "model": "B1",
                "readiness_score": 38.0,
                "readiness_status": "Not Ready",
                "risk_level": "high",
                "missing_count": 6,
                "completion_rate": 0.35,
            },
        ]
    )


def follow_up_rows():
    return pd.DataFrame(
        [
            {"source_url": "https://supplier-a.example.com/camera-b", "missing_field": "latency_ms"},
            {"source_url": "https://supplier-a.example.com/camera-b", "missing_field": "waterproof_rating"},
            {"source_url": "https://supplier-b.example.com/camera-c", "missing_field": "power_input"},
        ]
    )


def requirement_rows():
    return pd.DataFrame(
        [
            {"source_url": "https://supplier-a.example.com/camera-a", "current_value": "DC 10-32V"},
            {"source_url": "https://supplier-a.example.com/camera-a", "current_value": "IP69K"},
            {"source_url": "https://supplier-a.example.com/camera-b", "current_value": "2.4GHz"},
            {"source_url": "https://supplier-b.example.com/camera-c", "current_value": ""},
        ]
    )


def test_supplier_group_key_prefers_brand():
    row = {"source_url": "https://example.com/product", "brand": "Supplier A"}
    assert supplier_group_key(row) == "supplier a"


def test_supplier_group_key_falls_back_to_domain():
    row = {"source_url": "https://www.supplier-example.com/product", "brand": ""}
    assert supplier_group_key(row) == "supplier-example.com"


def test_supplier_status_for_score_english():
    assert supplier_status_for_score(85, language="en") == "Strong Candidate"
    assert supplier_status_for_score(70, language="en") == "Needs Follow-up"
    assert supplier_status_for_score(45, language="en") == "High Risk"
    assert supplier_status_for_score(30, language="en") == "Not Ready"


def test_supplier_status_for_score_chinese():
    assert supplier_status_for_score(85, language="zh-CN") == "强候选供应商"
    assert supplier_status_for_score(70, language="zh-CN") == "需要补充确认"


def test_build_supplier_comparison_aggregates_by_supplier():
    comparison = build_supplier_comparison(
        readiness_rows(),
        supplier_follow_up=follow_up_rows(),
        requirement_draft=requirement_rows(),
    )

    assert len(comparison) == 2
    assert list(comparison["supplier_name"])[0] == "Supplier A"
    assert comparison.loc[0, "product_count"] == 2
    assert comparison.loc[0, "ready_product_count"] == 1
    assert comparison.loc[0, "follow_up_required_count"] == 1


def test_supplier_comparison_counts_follow_ups_and_requirement_candidates():
    comparison = build_supplier_comparison(
        readiness_rows(),
        supplier_follow_up=follow_up_rows(),
        requirement_draft=requirement_rows(),
    )

    supplier_a = comparison[comparison["supplier_name"] == "Supplier A"].iloc[0]
    assert supplier_a["total_follow_up_questions"] == 2
    assert supplier_a["requirement_candidate_count"] == 3
    assert supplier_a["total_missing_fields"] == 4


def test_supplier_comparison_identifies_best_product():
    comparison = build_supplier_comparison(readiness_rows())
    supplier_a = comparison[comparison["supplier_name"] == "Supplier A"].iloc[0]

    assert supplier_a["best_product_title"] == "Camera A"
    assert supplier_a["best_product_url"] == "https://supplier-a.example.com/camera-a"
    assert supplier_a["max_readiness_score"] == 91.5


def test_supplier_comparison_supports_chinese_status_and_recommendation():
    comparison = build_supplier_comparison(readiness_rows(), language="zh-CN")

    assert "需要补充确认" in set(comparison["overall_status"]) or "强候选供应商" in set(comparison["overall_status"])
    assert comparison.loc[0, "recommendation"]


def test_supplier_comparison_handles_empty_input():
    comparison = build_supplier_comparison([])

    assert comparison.empty
    assert list(comparison.columns) == [
        "supplier_key",
        "supplier_name",
        "domain",
        "product_count",
        "average_readiness_score",
        "max_readiness_score",
        "average_completion_rate",
        "ready_product_count",
        "follow_up_required_count",
        "high_risk_product_count",
        "not_ready_product_count",
        "total_missing_fields",
        "total_follow_up_questions",
        "requirement_candidate_count",
        "best_product_title",
        "best_product_url",
        "overall_status",
        "recommendation",
        "next_action",
    ]

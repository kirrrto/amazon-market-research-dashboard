import pandas as pd

from src.products import build_product_pool_summary, product_pool_status_for_readiness


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
                "completion_rate": 0.9,
                "metadata_completeness": 1.0,
                "missing_count": 1,
                "required_fields_count": 10,
                "follow_up_question_count": 0,
                "requirement_candidate_count": 5,
                "missing_fields": "latency_ms",
                "missing_labels": "Latency",
            },
            {
                "source_url": "https://supplier-a.example.com/camera-b",
                "title": "Camera B",
                "brand": "Supplier A",
                "model": "A2",
                "readiness_score": 73.0,
                "readiness_status": "Follow-up Required",
                "risk_level": "medium",
                "completion_rate": 0.7,
                "metadata_completeness": 1.0,
                "missing_count": 3,
                "required_fields_count": 10,
                "follow_up_question_count": 2,
                "requirement_candidate_count": 3,
                "missing_fields": "waterproof_rating, latency_ms",
                "missing_labels": "Waterproof Rating, Latency",
            },
            {
                "source_url": "https://supplier-b.example.com/camera-c",
                "title": "Camera C",
                "brand": "Supplier B",
                "model": "B1",
                "readiness_score": 38.0,
                "readiness_status": "Not Ready",
                "risk_level": "high",
                "completion_rate": 0.35,
                "metadata_completeness": 0.75,
                "missing_count": 6,
                "required_fields_count": 10,
                "follow_up_question_count": 5,
                "requirement_candidate_count": 1,
                "missing_fields": "power_input, waterproof_rating",
                "missing_labels": "Power Input, Waterproof Rating",
            },
        ]
    )


def supplier_comparison_rows():
    return pd.DataFrame(
        [
            {
                "supplier_key": "supplier a",
                "supplier_name": "Supplier A",
                "domain": "supplier-a.example.com",
                "average_readiness_score": 82.25,
                "overall_status": "Strong Candidate",
            },
            {
                "supplier_key": "supplier b",
                "supplier_name": "Supplier B",
                "domain": "supplier-b.example.com",
                "average_readiness_score": 38.0,
                "overall_status": "Not Ready",
            },
        ]
    )


def supplier_follow_up_rows():
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
            {"source_url": "https://supplier-b.example.com/camera-c", "current_value": ""},
        ]
    )


def test_product_pool_status_for_readiness_english():
    assert product_pool_status_for_readiness(90, "low", language="en") == "Review Candidate"
    assert product_pool_status_for_readiness(70, "medium", language="en") == "Supplier Follow-up"
    assert product_pool_status_for_readiness(50, "high", language="en") == "Risk Review"
    assert product_pool_status_for_readiness(30, "medium", language="en") == "Hold"


def test_product_pool_status_for_readiness_chinese():
    assert product_pool_status_for_readiness(90, "low", language="zh-CN") == "评审候选"
    assert product_pool_status_for_readiness(70, "medium", language="zh-CN") == "供应商追问"


def test_build_product_pool_summary_preserves_product_and_supplier_context():
    pool = build_product_pool_summary(
        readiness_rows(),
        supplier_comparison=supplier_comparison_rows(),
    )

    assert len(pool) == 3
    assert list(pool["title"])[0] == "Camera A"
    assert pool.loc[0, "supplier_name"] == "Supplier A"
    assert pool.loc[0, "supplier_average_readiness_score"] == 82.25
    assert pool.loc[0, "supplier_overall_status"] == "Strong Candidate"


def test_product_pool_summary_sorts_by_priority_and_score():
    pool = build_product_pool_summary(readiness_rows())

    assert list(pool["priority"]) == ["P1", "P2", "P3"]
    assert list(pool["title"]) == ["Camera A", "Camera B", "Camera C"]


def test_product_pool_summary_uses_fallback_counts_when_missing_from_readiness():
    rows = readiness_rows().drop(
        columns=["follow_up_question_count", "requirement_candidate_count"]
    )
    pool = build_product_pool_summary(
        rows,
        supplier_follow_up=supplier_follow_up_rows(),
        requirement_draft=requirement_rows(),
    )

    camera_b = pool[pool["title"] == "Camera B"].iloc[0]
    camera_a = pool[pool["title"] == "Camera A"].iloc[0]

    assert camera_b["follow_up_question_count"] == 2
    assert camera_a["requirement_candidate_count"] == 2


def test_product_pool_summary_supports_chinese_labels():
    pool = build_product_pool_summary(readiness_rows(), language="zh-CN")

    assert "评审候选" in set(pool["product_pool_status"])
    assert "供应商追问" in set(pool["product_pool_status"])
    assert "P1" in set(pool["priority"])
    assert pool.loc[0, "recommendation"]


def test_product_pool_summary_falls_back_to_domain_for_supplier_name():
    rows = pd.DataFrame(
        [
            {
                "source_url": "https://www.domain-supplier.example.com/product",
                "title": "Camera D",
                "brand": "",
                "model": "",
                "readiness_score": 62,
                "readiness_status": "Follow-up Required",
                "risk_level": "medium",
            }
        ]
    )
    pool = build_product_pool_summary(rows)

    assert pool.loc[0, "supplier_key"] == "domain-supplier.example.com"
    assert pool.loc[0, "supplier_name"] == "domain-supplier.example.com"


def test_product_pool_summary_handles_empty_input():
    pool = build_product_pool_summary([])

    assert pool.empty
    assert list(pool.columns) == [
        "source_url",
        "title",
        "brand",
        "model",
        "supplier_key",
        "supplier_name",
        "domain",
        "readiness_score",
        "readiness_status",
        "product_pool_status",
        "priority",
        "risk_level",
        "completion_rate",
        "metadata_completeness",
        "missing_count",
        "required_fields_count",
        "follow_up_question_count",
        "requirement_candidate_count",
        "supplier_average_readiness_score",
        "supplier_overall_status",
        "recommendation",
        "next_action",
        "missing_fields",
        "missing_labels",
    ]

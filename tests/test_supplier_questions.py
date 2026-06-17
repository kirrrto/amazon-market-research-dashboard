import pandas as pd

from src.requirements import build_supplier_follow_up_questions, question_for_field


def gap_rows():
    return pd.DataFrame(
        [
            {
                "source_url": "https://supplier.example.com/a",
                "title": "Vehicle Camera A",
                "brand": "Brand A",
                "model": "A1",
                "profile": "vehicle_camera",
                "risk_level": "medium",
                "missing_fields": "waterproof_rating, latency_ms",
            },
            {
                "source_url": "https://supplier.example.com/b",
                "title": "Security Camera B",
                "brand": "Brand B",
                "model": "B1",
                "profile": "security_camera",
                "risk_level": "high",
                "missing_fields": "supports_rtsp",
            },
            {
                "source_url": "https://supplier.example.com/c",
                "title": "Complete Product",
                "brand": "Brand C",
                "model": "C1",
                "profile": "generic_hardware",
                "risk_level": "low",
                "missing_fields": "",
            },
        ]
    )


def test_question_for_known_field_english():
    question = question_for_field("waterproof_rating", "en")
    assert "waterproof rating" in question.lower()
    assert "IP" in question


def test_question_for_known_field_chinese():
    question = question_for_field("latency_ms", "zh-CN")
    assert "视频延迟" in question


def test_question_for_unknown_field_falls_back():
    assert question_for_field("custom_spec", "en") == "Please confirm the custom_spec specification for this product."
    assert "custom_spec" in question_for_field("custom_spec", "zh-CN")


def test_build_supplier_follow_up_questions_generates_one_row_per_missing_field():
    questions = build_supplier_follow_up_questions(gap_rows(), language="en")

    assert len(questions) == 3
    assert set(questions["missing_field"]) == {
        "waterproof_rating",
        "latency_ms",
        "supports_rtsp",
    }
    assert set(questions["status"]) == {"Open"}


def test_supplier_follow_up_questions_preserve_product_metadata():
    questions = build_supplier_follow_up_questions(gap_rows(), language="en")
    first = questions[questions["missing_field"] == "waterproof_rating"].iloc[0]

    assert first["source_url"] == "https://supplier.example.com/a"
    assert first["title"] == "Vehicle Camera A"
    assert first["profile"] == "vehicle_camera"
    assert first["priority"] == "Medium"


def test_supplier_follow_up_questions_support_chinese_labels():
    questions = build_supplier_follow_up_questions(gap_rows(), language="zh-CN")

    assert "防水等级" in set(questions["missing_label"])
    assert "延迟" in set(questions["missing_label"])
    assert set(questions["status"]) == {"待处理"}
    assert "高" in set(questions["priority"])


def test_supplier_follow_up_questions_handles_empty_input():
    questions = build_supplier_follow_up_questions([], language="en")
    assert questions.empty
    assert list(questions.columns) == [
        "source_url",
        "title",
        "brand",
        "model",
        "profile",
        "risk_level",
        "missing_field",
        "missing_label",
        "question",
        "priority",
        "owner",
        "status",
        "notes",
    ]

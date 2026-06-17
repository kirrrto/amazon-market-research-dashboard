import pandas as pd

from src.requirements import RequirementDraftRow, build_requirement_draft


def matrix():
    return pd.DataFrame(
        [
            {
                "source_url": "https://supplier.example.com/a",
                "title": "Vehicle Camera A",
                "brand": "Brand A",
                "model": "A1",
                "power_input": "DC 10-32V",
                "operating_temperature": "-20°C to 70°C",
                "waterproof_rating": "",
            },
            {
                "source_url": "https://supplier.example.com/b",
                "title": "Vehicle Camera B",
                "brand": "Brand B",
                "model": "B1",
                "power_input": "",
                "operating_temperature": "",
                "waterproof_rating": "IP69K",
            },
        ]
    )


def gaps():
    return pd.DataFrame(
        [
            {
                "source_url": "https://supplier.example.com/a",
                "profile": "vehicle_camera",
                "risk_level": "medium",
            },
            {
                "source_url": "https://supplier.example.com/b",
                "profile": "vehicle_camera",
                "risk_level": "high",
            },
        ]
    )


def test_requirement_draft_row_as_dict():
    row = RequirementDraftRow(
        source_url="https://example.com",
        title="Camera",
        brand="Brand",
        model="A1",
        profile="vehicle_camera",
        risk_level="medium",
        requirement_field="power_input",
        requirement_label="Power Input",
        current_value="DC 10-32V",
        evidence_source="Specification Matrix",
        action="Keep as candidate requirement",
    )

    assert row.as_dict()["requirement_field"] == "power_input"
    assert row.as_dict()["current_value"] == "DC 10-32V"


def test_build_requirement_draft_generates_rows_from_matrix():
    draft = build_requirement_draft(
        matrix(),
        gap_analysis=gaps(),
        profile="vehicle_camera",
        fields=["power_input", "operating_temperature", "waterproof_rating"],
    )

    assert len(draft) == 6
    assert set(draft["profile"]) == {"vehicle_camera"}
    assert set(draft["risk_level"]) == {"medium", "high"}

    first_power = draft[
        (draft["source_url"] == "https://supplier.example.com/a")
        & (draft["requirement_field"] == "power_input")
    ].iloc[0]
    assert first_power["current_value"] == "DC 10-32V"
    assert first_power["evidence_source"] == "Specification Matrix"
    assert first_power["action"] == "Keep as candidate requirement"


def test_missing_values_use_gap_analysis_action():
    draft = build_requirement_draft(
        matrix(),
        gap_analysis=gaps(),
        profile="vehicle_camera",
        fields=["power_input", "operating_temperature", "waterproof_rating"],
    )

    missing_power = draft[
        (draft["source_url"] == "https://supplier.example.com/b")
        & (draft["requirement_field"] == "power_input")
    ].iloc[0]
    assert missing_power["current_value"] == ""
    assert missing_power["evidence_source"] == "Gap Analysis"
    assert missing_power["action"] == "Required before product definition"


def test_requirement_draft_supports_chinese_labels_and_actions():
    draft = build_requirement_draft(
        matrix(),
        gap_analysis=gaps(),
        profile="vehicle_camera",
        fields=["power_input", "waterproof_rating"],
        language="zh-CN",
    )

    assert "供电输入" in set(draft["requirement_label"])
    assert "防水等级" in set(draft["requirement_label"])
    assert "保留为候选需求" in set(draft["action"])
    assert "产品定义前必须确认" in set(draft["action"])


def test_requirement_draft_handles_empty_matrix():
    draft = build_requirement_draft(pd.DataFrame(), profile="vehicle_camera")
    assert draft.empty
    assert list(draft.columns) == [
        "source_url",
        "title",
        "brand",
        "model",
        "profile",
        "risk_level",
        "requirement_field",
        "requirement_label",
        "current_value",
        "evidence_source",
        "action",
        "notes",
    ]


def test_requirement_draft_uses_unknown_risk_when_gaps_missing():
    draft = build_requirement_draft(
        matrix(),
        profile="vehicle_camera",
        fields=["power_input"],
    )
    assert set(draft["risk_level"]) == {"unknown"}

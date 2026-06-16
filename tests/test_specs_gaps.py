import pandas as pd
import pytest

from src.specs import (
    build_gap_analysis,
    get_spec_profile,
    list_spec_profiles,
    risk_level_for_missing_count,
)


def matrix_rows():
    return pd.DataFrame(
        [
            {
                "source_url": "https://supplier.example.com/a",
                "title": "Vehicle Camera A",
                "brand": "Brand A",
                "model": "A1",
                "power_input": "DC 10-32V",
                "operating_temperature": "-20°C to 70°C",
                "dimensions": "140 × 120 × 40 mm",
                "camera_resolution": "1080P",
                "monitor_size": "7 inch",
                "waterproof_rating": "IP69K",
                "wireless_protocol": "2.4GHz",
                "latency_ms": "",
                "transmission_range_m": "",
            },
            {
                "source_url": "https://supplier.example.com/b",
                "title": "Vehicle Camera B",
                "brand": "Brand B",
                "model": "B1",
                "power_input": "",
                "operating_temperature": "",
                "dimensions": "",
                "camera_resolution": "",
                "monitor_size": "",
                "waterproof_rating": "",
                "wireless_protocol": "",
                "latency_ms": "",
                "transmission_range_m": "",
            },
        ]
    )


def test_spec_profiles_include_required_profiles():
    profile_ids = {profile.profile_id for profile in list_spec_profiles()}
    assert {"generic_hardware", "security_camera", "vehicle_camera"}.issubset(profile_ids)


def test_get_unknown_profile_raises_key_error():
    with pytest.raises(KeyError):
        get_spec_profile("missing_profile")


def test_risk_level_thresholds():
    assert risk_level_for_missing_count(0) == "low"
    assert risk_level_for_missing_count(1) == "low"
    assert risk_level_for_missing_count(2) == "medium"
    assert risk_level_for_missing_count(3) == "medium"
    assert risk_level_for_missing_count(4) == "high"


def test_generic_hardware_gap_analysis():
    gaps = build_gap_analysis(matrix_rows(), profile="generic_hardware")

    first = gaps[gaps["source_url"] == "https://supplier.example.com/a"].iloc[0]
    assert first["missing_count"] == 0
    assert first["completion_rate"] == 1.0
    assert first["risk_level"] == "low"

    second = gaps[gaps["source_url"] == "https://supplier.example.com/b"].iloc[0]
    assert second["missing_count"] == 3
    assert second["risk_level"] == "medium"
    assert "power_input" in second["missing_fields"]


def test_vehicle_camera_gap_analysis_high_risk():
    gaps = build_gap_analysis(matrix_rows(), profile="vehicle_camera")

    first = gaps[gaps["source_url"] == "https://supplier.example.com/a"].iloc[0]
    assert first["missing_count"] == 2
    assert first["risk_level"] == "medium"
    assert "latency_ms" in first["missing_fields"]
    assert "transmission_range_m" in first["missing_fields"]

    second = gaps[gaps["source_url"] == "https://supplier.example.com/b"].iloc[0]
    assert second["missing_count"] == 8
    assert second["risk_level"] == "high"


def test_gap_analysis_supports_chinese_labels():
    gaps = build_gap_analysis(matrix_rows(), profile="vehicle_camera", language="zh-CN")
    first = gaps.iloc[0]

    assert first["profile_label"] == "车载影像"
    assert "延迟" in first["missing_labels"]


def test_gap_analysis_handles_missing_columns_as_missing_fields():
    matrix = pd.DataFrame(
        [
            {
                "source_url": "https://supplier.example.com/c",
                "title": "Simple Product",
            }
        ]
    )
    gaps = build_gap_analysis(matrix, profile="generic_hardware")

    assert gaps.loc[0, "missing_count"] == 3
    assert gaps.loc[0, "completion_rate"] == 0.0


def test_gap_analysis_empty_matrix_returns_expected_columns():
    gaps = build_gap_analysis(pd.DataFrame(), profile="generic_hardware")
    assert list(gaps.columns) == [
        "source_url",
        "title",
        "brand",
        "model",
        "profile",
        "profile_label",
        "missing_fields",
        "missing_labels",
        "missing_count",
        "required_fields_count",
        "completion_rate",
        "risk_level",
    ]
    assert gaps.empty

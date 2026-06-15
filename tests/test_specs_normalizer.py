import pytest

from src.specs import (
    find_standard_field,
    get_spec_field,
    list_spec_fields,
    normalize_alias_key,
    normalize_raw_specifications,
    normalize_spec_value,
)


def test_spec_dictionary_contains_core_hardware_fields():
    fields = {field.standard_field for field in list_spec_fields()}
    assert {
        "power_input",
        "operating_temperature",
        "waterproof_rating",
        "resolution",
        "dimensions",
        "battery_capacity_mah",
        "supports_rtsp",
        "supports_onvif",
    }.issubset(fields)


def test_get_unknown_spec_field_raises_key_error():
    with pytest.raises(KeyError):
        get_spec_field("missing_field")


def test_alias_normalization_handles_punctuation_and_case():
    assert normalize_alias_key("Power Supply") == normalize_alias_key("power-supply")
    assert normalize_alias_key("工作温度") == normalize_alias_key(" 工作 温度 ")


def test_exact_alias_matches_standard_field():
    assert find_standard_field("Power Supply") == ("power_input", 1.0)
    assert find_standard_field("Operating Temperature") == ("operating_temperature", 1.0)
    assert find_standard_field("Waterproof Rating") == ("waterproof_rating", 1.0)


def test_chinese_alias_matches_standard_field():
    assert find_standard_field("供电输入") == ("power_input", 1.0)
    assert find_standard_field("防水等级") == ("waterproof_rating", 1.0)
    assert find_standard_field("电池容量") == ("battery_capacity_mah", 1.0)


def test_containment_match_handles_supplier_specific_names():
    field, confidence = find_standard_field("Dimension of Multiplexer Box")
    assert field == "dimensions"
    assert confidence >= 0.8


def test_unknown_alias_returns_none():
    assert find_standard_field("Marketing Features") == (None, 0.0)


def test_normalizes_power_input():
    assert normalize_spec_value("power_input", "DC：10-32V") == "DC 10-32V"


def test_normalizes_temperature_range():
    assert normalize_spec_value("operating_temperature", "-20℃～70℃") == "-20°C to 70°C"


def test_normalizes_waterproof_rating():
    assert normalize_spec_value("waterproof_rating", "waterproof IP 69K") == "IP69K"


def test_normalizes_battery_capacity():
    assert normalize_spec_value("battery_capacity_mah", "5200mAh rechargeable battery") == "5200 mAh"


def test_normalizes_boolean_support_fields():
    assert normalize_spec_value("supports_rtsp", "支持") == "Yes"
    assert normalize_spec_value("supports_onvif", "不支持") == "No"


def test_normalize_raw_specifications_preserves_evidence():
    rows = normalize_raw_specifications(
        [
            {
                "source_url": "https://example.com/product",
                "spec_name": "Power Supply",
                "spec_value": "DC：10-32V",
                "parser": "html.table",
                "fetched_at": "2026-01-01T00:00:00+00:00",
            },
            {
                "source_url": "https://example.com/product",
                "spec_name": "Marketing Features",
                "spec_value": "Great product",
                "parser": "html.table",
                "fetched_at": "2026-01-01T00:00:00+00:00",
            },
        ],
        language="zh-CN",
    )

    assert len(rows) == 1
    row = rows[0]
    assert row["standard_field"] == "power_input"
    assert row["standard_label"] == "供电输入"
    assert row["raw_spec_name"] == "Power Supply"
    assert row["normalized_value"] == "DC 10-32V"
    assert row["category"] == "electrical"
    assert row["parser"] == "html.table"

import pandas as pd

from src.specs import build_specification_matrix, matrix_field_columns


def normalized_rows():
    return [
        {
            "source_url": "https://supplier.example.com/a",
            "standard_field": "power_input",
            "normalized_value": "DC 10-32V",
            "confidence": 1.0,
        },
        {
            "source_url": "https://supplier.example.com/a",
            "standard_field": "operating_temperature",
            "normalized_value": "-20°C to 70°C",
            "confidence": 1.0,
        },
        {
            "source_url": "https://supplier.example.com/b",
            "standard_field": "waterproof_rating",
            "normalized_value": "IP69K",
            "confidence": 1.0,
        },
    ]


def product_rows():
    return [
        {
            "source_url": "https://supplier.example.com/a",
            "title": "HD Video Multiplexer",
            "brand": "STONKAM",
            "model": "HMU318",
        },
        {
            "source_url": "https://supplier.example.com/b",
            "title": "1080P License Plate Camera",
            "brand": "STONKAM",
            "model": "FHD642M",
        },
    ]


def test_matrix_field_columns_preserve_custom_order():
    assert matrix_field_columns(["power_input", "power_input", "resolution"]) == [
        "power_input",
        "resolution",
    ]


def test_build_specification_matrix_from_records():
    matrix = build_specification_matrix(
        normalized_rows(),
        products=product_rows(),
        fields=["power_input", "operating_temperature", "waterproof_rating"],
    )

    assert list(matrix.columns) == [
        "source_url",
        "title",
        "brand",
        "model",
        "power_input",
        "operating_temperature",
        "waterproof_rating",
    ]
    assert len(matrix) == 2

    first = matrix[matrix["source_url"] == "https://supplier.example.com/a"].iloc[0]
    assert first["title"] == "HD Video Multiplexer"
    assert first["power_input"] == "DC 10-32V"
    assert first["operating_temperature"] == "-20°C to 70°C"
    assert first["waterproof_rating"] == ""


def test_build_specification_matrix_accepts_dataframes():
    matrix = build_specification_matrix(
        pd.DataFrame(normalized_rows()),
        products=pd.DataFrame(product_rows()),
        fields=["power_input", "operating_temperature", "waterproof_rating"],
    )

    second = matrix[matrix["source_url"] == "https://supplier.example.com/b"].iloc[0]
    assert second["model"] == "FHD642M"
    assert second["waterproof_rating"] == "IP69K"


def test_matrix_keeps_urls_even_when_metadata_is_missing():
    matrix = build_specification_matrix(
        [
            {
                "source_url": "https://supplier.example.com/no-meta",
                "standard_field": "resolution",
                "normalized_value": "1080P",
                "confidence": 1.0,
            }
        ],
        fields=["resolution"],
    )

    assert matrix.loc[0, "source_url"] == "https://supplier.example.com/no-meta"
    assert matrix.loc[0, "title"] == ""
    assert matrix.loc[0, "resolution"] == "1080P"


def test_higher_confidence_value_wins_for_duplicate_fields():
    matrix = build_specification_matrix(
        [
            {
                "source_url": "https://supplier.example.com/a",
                "standard_field": "power_input",
                "normalized_value": "DC 12V",
                "confidence": 0.6,
            },
            {
                "source_url": "https://supplier.example.com/a",
                "standard_field": "power_input",
                "normalized_value": "DC 10-32V",
                "confidence": 1.0,
            },
        ],
        fields=["power_input"],
    )

    assert matrix.loc[0, "power_input"].startswith("DC 10-32V")


def test_equal_confidence_duplicate_values_are_auditable():
    matrix = build_specification_matrix(
        [
            {
                "source_url": "https://supplier.example.com/a",
                "standard_field": "wireless_protocol",
                "normalized_value": "2.4GHz",
                "confidence": 1.0,
            },
            {
                "source_url": "https://supplier.example.com/a",
                "standard_field": "wireless_protocol",
                "normalized_value": "Digital wireless",
                "confidence": 1.0,
            },
        ],
        fields=["wireless_protocol"],
    )

    assert matrix.loc[0, "wireless_protocol"] == "Digital wireless | 2.4GHz"


def test_empty_spec_values_are_ignored():
    matrix = build_specification_matrix(
        [
            {
                "source_url": "https://supplier.example.com/a",
                "standard_field": "power_input",
                "normalized_value": "",
                "confidence": 1.0,
            }
        ],
        fields=["power_input"],
    )

    assert matrix.loc[0, "power_input"] == ""

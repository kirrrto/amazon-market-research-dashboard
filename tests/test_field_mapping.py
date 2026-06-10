import pandas as pd
import pytest

from src.importers.mapping import (
    FieldMappingError,
    apply_field_mapping,
    suggest_field_mappings,
    validate_field_mapping,
)


def complete_mapping():
    return {
        "asin": "ASIN",
        "title": "Product Name",
        "brand": "品牌名称",
        "price": "Current Price",
        "rating": "Star Rating",
        "reviews": "Review Count",
        "monthly_sales": "月销量",
        "category": "Product Type",
    }


def test_suggests_english_and_chinese_columns():
    suggestions = suggest_field_mappings(complete_mapping().values())
    assert suggestions == complete_mapping()


def test_suggests_normalized_header_variants():
    columns = [
        "Product-ASIN",
        "Product_Title",
        "Brand Name",
        "Sale Price",
        "Average Rating",
        "Number of Reviews",
        "Estimated Monthly Sales",
        "Product Category",
    ]
    suggestions = suggest_field_mappings(columns)
    assert all(suggestions.values())


def test_rejects_missing_required_mapping():
    mapping = complete_mapping()
    mapping["monthly_sales"] = None
    with pytest.raises(FieldMappingError, match="monthly_sales"):
        validate_field_mapping(mapping, complete_mapping().values())


def test_rejects_duplicate_source_assignment():
    mapping = complete_mapping()
    mapping["rating"] = mapping["price"]
    with pytest.raises(FieldMappingError, match="assigned once"):
        validate_field_mapping(mapping, complete_mapping().values())


def test_rejects_missing_source_column():
    mapping = complete_mapping()
    mapping["price"] = "Not Present"
    with pytest.raises(FieldMappingError, match="do not exist"):
        validate_field_mapping(mapping, complete_mapping().values())


def test_applies_mapping_without_extra_columns():
    frame = pd.DataFrame(
        {
            **{column: ["value"] for column in complete_mapping().values()},
            "Internal note": ["ignore"],
        }
    )
    result = apply_field_mapping(frame, complete_mapping())
    assert list(result.columns) == list(complete_mapping())
    assert "Internal note" not in result.columns

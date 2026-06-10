import pandas as pd
import pytest

from src.analysis import (
    brand_summary,
    clean_market_data,
    clean_market_data_with_report,
    summarize_market,
    validate_columns,
)


def sample_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "asin": "A1",
                "title": "Camera A",
                "brand": "Brand A",
                "price": 50,
                "rating": 4.0,
                "reviews": 100,
                "monthly_sales": 20,
                "category": "Camera",
            },
            {
                "asin": "A2",
                "title": "Camera B",
                "brand": "Brand B",
                "price": 100,
                "rating": 3.5,
                "reviews": 20,
                "monthly_sales": 10,
                "category": "Camera",
            },
        ]
    )


def test_validate_columns_returns_missing_fields():
    missing = validate_columns(["asin", "title"])
    assert "brand" in missing
    assert "monthly_sales" in missing


def test_clean_market_data_adds_calculated_columns():
    result = clean_market_data(sample_frame())
    assert "estimated_monthly_revenue" in result.columns
    assert "opportunity_score" in result.columns
    assert result["opportunity_score"].between(0, 100).all()


def test_clean_market_data_rejects_missing_columns():
    with pytest.raises(ValueError):
        clean_market_data(pd.DataFrame([{"asin": "A1"}]))


def test_summary_calculation():
    result = clean_market_data(sample_frame())
    summary = summarize_market(result)

    assert summary.product_count == 2
    assert summary.average_price == 75.0
    assert summary.estimated_monthly_revenue == 2000.0
    assert summary.top_brand_share == 0.5


def test_brand_summary_orders_by_revenue():
    result = clean_market_data(sample_frame())
    summary = brand_summary(result)
    assert summary.iloc[0]["brand"] in {"Brand A", "Brand B"}
    assert summary["revenue_share"].sum() == pytest.approx(1.0)



def test_common_marketplace_numeric_formats_are_parsed():
    data = sample_frame().astype(
        {
            "price": "object",
            "rating": "object",
            "reviews": "object",
            "monthly_sales": "object",
        }
    )
    data.loc[0, "price"] = "$1,299.99"
    data.loc[0, "rating"] = "4.5 out of 5"
    data.loc[0, "reviews"] = "1,234"
    data.loc[0, "monthly_sales"] = "2,500"

    result = clean_market_data(data)

    assert result.loc[0, "price"] == pytest.approx(1299.99)
    assert result.loc[0, "rating"] == pytest.approx(4.5)
    assert result.loc[0, "reviews"] == pytest.approx(1234)
    assert result.loc[0, "monthly_sales"] == pytest.approx(2500)


def test_cleaning_report_tracks_dropped_and_normalized_values():
    data = pd.DataFrame(
        [
            {
                "asin": "a1",
                "title": "Camera A",
                "brand": " ",
                "price": "$50",
                "rating": 6,
                "reviews": -5,
                "monthly_sales": 20,
                "category": "",
            },
            {
                "asin": "A1",
                "title": "Duplicate",
                "brand": "Brand A",
                "price": 55,
                "rating": 4,
                "reviews": 10,
                "monthly_sales": 5,
                "category": "Camera",
            },
            {
                "asin": "A3",
                "title": "Invalid",
                "brand": "Brand B",
                "price": "not available",
                "rating": 4,
                "reviews": 10,
                "monthly_sales": 5,
                "category": "Camera",
            },
            {
                "asin": "",
                "title": "Missing ASIN",
                "brand": "Brand C",
                "price": 40,
                "rating": 4,
                "reviews": 10,
                "monthly_sales": 5,
                "category": "Camera",
            },
        ]
    )

    result, report = clean_market_data_with_report(data)

    assert len(result) == 1
    assert result.loc[0, "asin"] == "A1"
    assert result.loc[0, "brand"] == "Unknown"
    assert result.loc[0, "category"] == "Uncategorized"
    assert result.loc[0, "rating"] == 5
    assert result.loc[0, "reviews"] == 0
    assert report.dropped_missing_asin == 1
    assert report.dropped_invalid_numeric == 1
    assert report.dropped_duplicates == 1
    assert report.normalized_out_of_range_values == 2
    assert report.normalized_blank_brands == 1
    assert report.normalized_blank_categories == 1


def test_all_invalid_rows_raise_clear_error():
    data = sample_frame()
    data["price"] = "not available"

    with pytest.raises(ValueError, match="No valid product rows remain"):
        clean_market_data(data)


def test_duplicate_columns_after_normalization_are_rejected():
    data = sample_frame()
    data[" Price "] = data["price"]

    with pytest.raises(ValueError, match="Duplicate columns after normalization"):
        clean_market_data(data)

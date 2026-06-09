import pandas as pd
import pytest

from src.analysis import (
    brand_summary,
    clean_market_data,
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

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd


REQUIRED_COLUMNS = {
    "asin",
    "title",
    "brand",
    "price",
    "rating",
    "reviews",
    "monthly_sales",
    "category",
}

NUMERIC_COLUMNS = ["price", "rating", "reviews", "monthly_sales"]


@dataclass(frozen=True)
class MarketSummary:
    product_count: int
    average_price: float
    median_reviews: float
    estimated_monthly_revenue: float
    top_brand_share: float


def validate_columns(columns: Iterable[str]) -> list[str]:
    normalized = {str(column).strip().lower() for column in columns}
    return sorted(REQUIRED_COLUMNS - normalized)


def clean_market_data(raw: pd.DataFrame) -> pd.DataFrame:
    data = raw.copy()
    data.columns = [str(column).strip().lower() for column in data.columns]

    missing = validate_columns(data.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    for column in NUMERIC_COLUMNS:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    data["brand"] = data["brand"].fillna("Unknown").astype(str).str.strip()
    data["category"] = data["category"].fillna("Uncategorized").astype(str).str.strip()
    data["title"] = data["title"].fillna("").astype(str).str.strip()
    data["asin"] = data["asin"].fillna("").astype(str).str.strip()

    data["price"] = data["price"].clip(lower=0)
    data["rating"] = data["rating"].clip(lower=0, upper=5)
    data["reviews"] = data["reviews"].clip(lower=0)
    data["monthly_sales"] = data["monthly_sales"].clip(lower=0)

    data = data.dropna(subset=["price", "rating", "reviews", "monthly_sales"])
    data = data[data["asin"] != ""].drop_duplicates(subset=["asin"], keep="first")

    data["estimated_monthly_revenue"] = data["price"] * data["monthly_sales"]
    data["opportunity_score"] = calculate_opportunity_score(data)

    return data.reset_index(drop=True)


def _min_max(series: pd.Series, reverse: bool = False) -> pd.Series:
    values = series.astype(float)
    min_value = float(values.min())
    max_value = float(values.max())

    if np.isclose(min_value, max_value):
        normalized = pd.Series(np.full(len(values), 0.5), index=series.index)
    else:
        normalized = (values - min_value) / (max_value - min_value)

    return 1 - normalized if reverse else normalized


def calculate_opportunity_score(data: pd.DataFrame) -> pd.Series:
    demand = _min_max(data["monthly_sales"])
    low_review_barrier = _min_max(np.log1p(data["reviews"]), reverse=True)
    rating_gap = ((5 - data["rating"]) / 5).clip(0, 1)
    price_room = _min_max(data["price"])

    brand_revenue = data.groupby("brand")["estimated_monthly_revenue"].transform("sum")
    total_revenue = max(float(data["estimated_monthly_revenue"].sum()), 1.0)
    low_brand_concentration = 1 - (brand_revenue / total_revenue).clip(0, 1)

    score = (
        demand * 0.35
        + low_review_barrier * 0.25
        + rating_gap * 0.15
        + low_brand_concentration * 0.15
        + price_room * 0.10
    ) * 100

    return score.round(1)


def summarize_market(data: pd.DataFrame) -> MarketSummary:
    if data.empty:
        return MarketSummary(0, 0.0, 0.0, 0.0, 0.0)

    brand_revenue = (
        data.groupby("brand", dropna=False)["estimated_monthly_revenue"]
        .sum()
        .sort_values(ascending=False)
    )
    total_revenue = float(brand_revenue.sum())
    top_brand_share = float(brand_revenue.iloc[0] / total_revenue) if total_revenue else 0.0

    return MarketSummary(
        product_count=int(len(data)),
        average_price=round(float(data["price"].mean()), 2),
        median_reviews=round(float(data["reviews"].median()), 0),
        estimated_monthly_revenue=round(float(data["estimated_monthly_revenue"].sum()), 2),
        top_brand_share=round(top_brand_share, 4),
    )


def brand_summary(data: pd.DataFrame) -> pd.DataFrame:
    if data.empty:
        return pd.DataFrame(
            columns=[
                "brand",
                "products",
                "average_price",
                "monthly_sales",
                "estimated_monthly_revenue",
                "revenue_share",
            ]
        )

    result = (
        data.groupby("brand", as_index=False)
        .agg(
            products=("asin", "count"),
            average_price=("price", "mean"),
            monthly_sales=("monthly_sales", "sum"),
            estimated_monthly_revenue=("estimated_monthly_revenue", "sum"),
        )
        .sort_values("estimated_monthly_revenue", ascending=False)
    )

    total = max(float(result["estimated_monthly_revenue"].sum()), 1.0)
    result["revenue_share"] = result["estimated_monthly_revenue"] / total
    result["average_price"] = result["average_price"].round(2)
    result["estimated_monthly_revenue"] = result["estimated_monthly_revenue"].round(2)
    result["revenue_share"] = result["revenue_share"].round(4)
    return result.reset_index(drop=True)


def price_band_summary(data: pd.DataFrame) -> pd.DataFrame:
    if data.empty:
        return pd.DataFrame(columns=["price_band", "products", "monthly_sales"])

    bins = [-np.inf, 29.99, 49.99, 79.99, 119.99, np.inf]
    labels = ["<$30", "$30–49.99", "$50–79.99", "$80–119.99", "$120+"]

    working = data.copy()
    working["price_band"] = pd.cut(working["price"], bins=bins, labels=labels)

    return (
        working.groupby("price_band", observed=False, as_index=False)
        .agg(products=("asin", "count"), monthly_sales=("monthly_sales", "sum"))
    )

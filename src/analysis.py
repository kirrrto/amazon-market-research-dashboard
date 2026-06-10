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


@dataclass(frozen=True)
class CleaningReport:
    """Summary of automatic changes made while importing market data."""

    input_rows: int
    output_rows: int
    dropped_missing_asin: int
    dropped_invalid_numeric: int
    dropped_duplicates: int
    normalized_out_of_range_values: int
    normalized_blank_brands: int
    normalized_blank_categories: int

    @property
    def changed_rows_or_values(self) -> int:
        return (
            self.dropped_missing_asin
            + self.dropped_invalid_numeric
            + self.dropped_duplicates
            + self.normalized_out_of_range_values
            + self.normalized_blank_brands
            + self.normalized_blank_categories
        )

    def messages(self) -> list[str]:
        details: list[str] = []
        if self.dropped_missing_asin:
            details.append(f"{self.dropped_missing_asin} row(s) without an ASIN")
        if self.dropped_invalid_numeric:
            details.append(f"{self.dropped_invalid_numeric} row(s) with invalid numeric data")
        if self.dropped_duplicates:
            details.append(f"{self.dropped_duplicates} duplicate ASIN row(s)")
        if self.normalized_out_of_range_values:
            details.append(
                f"{self.normalized_out_of_range_values} out-of-range numeric value(s)"
            )
        if self.normalized_blank_brands:
            details.append(f"{self.normalized_blank_brands} blank brand value(s)")
        if self.normalized_blank_categories:
            details.append(f"{self.normalized_blank_categories} blank category value(s)")
        return details


def validate_columns(columns: Iterable[str]) -> list[str]:
    normalized = {str(column).strip().lower() for column in columns}
    return sorted(REQUIRED_COLUMNS - normalized)


def _parse_numeric(series: pd.Series) -> pd.Series:
    """Parse common marketplace numeric formats such as '$79.99' and '1,234'."""

    text = series.astype("string").str.strip()
    text = text.str.replace(",", "", regex=False)
    text = text.str.replace("$", "", regex=False)
    text = text.str.replace("%", "", regex=False)

    # Extract the first numeric token so values such as "4.5 out of 5" remain usable.
    extracted = text.str.extract(r"([-+]?(?:\d+(?:\.\d*)?|\.\d+))", expand=False)
    return pd.to_numeric(extracted, errors="coerce")


def clean_market_data(raw: pd.DataFrame) -> pd.DataFrame:
    data, _ = clean_market_data_with_report(raw)
    return data


def clean_market_data_with_report(
    raw: pd.DataFrame,
) -> tuple[pd.DataFrame, CleaningReport]:
    data = raw.copy()
    input_rows = int(len(data))
    data.columns = [str(column).strip().lower() for column in data.columns]

    if data.columns.duplicated().any():
        duplicates = sorted(set(data.columns[data.columns.duplicated()].tolist()))
        raise ValueError(
            "Duplicate columns after normalization: " + ", ".join(duplicates)
        )

    missing = validate_columns(data.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    for column in NUMERIC_COLUMNS:
        data[column] = _parse_numeric(data[column])

    data["asin"] = data["asin"].fillna("").astype(str).str.strip().str.upper()
    data["title"] = data["title"].fillna("").astype(str).str.strip()
    data["brand"] = data["brand"].fillna("").astype(str).str.strip()
    data["category"] = data["category"].fillna("").astype(str).str.strip()

    blank_brand_mask = data["brand"].eq("")
    blank_category_mask = data["category"].eq("")
    normalized_blank_brands = int(blank_brand_mask.sum())
    normalized_blank_categories = int(blank_category_mask.sum())
    data.loc[blank_brand_mask, "brand"] = "Unknown"
    data.loc[blank_category_mask, "category"] = "Uncategorized"

    missing_asin_mask = data["asin"].eq("")
    invalid_numeric_mask = data[NUMERIC_COLUMNS].isna().any(axis=1)
    dropped_missing_asin = int(missing_asin_mask.sum())
    dropped_invalid_numeric = int((invalid_numeric_mask & ~missing_asin_mask).sum())

    data = data.loc[~missing_asin_mask & ~invalid_numeric_mask].copy()

    out_of_range_count = int(
        (data["price"] < 0).sum()
        + (data["reviews"] < 0).sum()
        + (data["monthly_sales"] < 0).sum()
        + ((data["rating"] < 0) | (data["rating"] > 5)).sum()
    )

    data["price"] = data["price"].clip(lower=0)
    data["rating"] = data["rating"].clip(lower=0, upper=5)
    data["reviews"] = data["reviews"].clip(lower=0)
    data["monthly_sales"] = data["monthly_sales"].clip(lower=0)

    duplicate_mask = data.duplicated(subset=["asin"], keep="first")
    dropped_duplicates = int(duplicate_mask.sum())
    data = data.loc[~duplicate_mask].copy()

    if data.empty:
        raise ValueError("No valid product rows remain after cleaning.")

    data["estimated_monthly_revenue"] = data["price"] * data["monthly_sales"]
    data["opportunity_score"] = calculate_opportunity_score(data)
    data = data.reset_index(drop=True)

    report = CleaningReport(
        input_rows=input_rows,
        output_rows=int(len(data)),
        dropped_missing_asin=dropped_missing_asin,
        dropped_invalid_numeric=dropped_invalid_numeric,
        dropped_duplicates=dropped_duplicates,
        normalized_out_of_range_values=out_of_range_count,
        normalized_blank_brands=normalized_blank_brands,
        normalized_blank_categories=normalized_blank_categories,
    )
    return data, report


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

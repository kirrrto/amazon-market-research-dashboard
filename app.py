from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.analysis import (
    brand_summary,
    clean_market_data,
    price_band_summary,
    summarize_market,
)

st.set_page_config(page_title="Amazon Market Research Dashboard", layout="wide")

st.title("Amazon Market Research Dashboard")
st.caption("Upload a product research CSV to evaluate demand, competition and market structure.")

sample_path = Path(__file__).parent / "data" / "sample_products.csv"

with st.sidebar:
    st.header("Data source")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    use_sample = st.checkbox("Use included sample data", value=uploaded_file is None)

try:
    if uploaded_file is not None:
        raw_data = pd.read_csv(uploaded_file)
    elif use_sample:
        raw_data = pd.read_csv(sample_path)
    else:
        st.info("Upload a CSV or enable sample data.")
        st.stop()

    data = clean_market_data(raw_data)

except (ValueError, pd.errors.ParserError, UnicodeDecodeError) as exc:
    st.error(f"Unable to process file: {exc}")
    st.stop()

categories = sorted(data["category"].dropna().unique().tolist())
brands = sorted(data["brand"].dropna().unique().tolist())

with st.sidebar:
    selected_categories = st.multiselect("Categories", categories, default=categories)
    selected_brands = st.multiselect("Brands", brands, default=brands)

filtered = data[
    data["category"].isin(selected_categories)
    & data["brand"].isin(selected_brands)
].copy()

summary = summarize_market(filtered)

metric_1, metric_2, metric_3, metric_4, metric_5 = st.columns(5)
metric_1.metric("Products", f"{summary.product_count}")
metric_2.metric("Average price", f"${summary.average_price:,.2f}")
metric_3.metric("Median reviews", f"{summary.median_reviews:,.0f}")
metric_4.metric("Estimated monthly revenue", f"${summary.estimated_monthly_revenue:,.0f}")
metric_5.metric("Top brand share", f"{summary.top_brand_share:.1%}")

st.subheader("Highest opportunity products")
opportunities = filtered.sort_values(
    ["opportunity_score", "estimated_monthly_revenue"],
    ascending=False,
)
st.dataframe(
    opportunities[
        [
            "asin",
            "title",
            "brand",
            "price",
            "rating",
            "reviews",
            "monthly_sales",
            "estimated_monthly_revenue",
            "opportunity_score",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)

left, right = st.columns(2)

with left:
    st.subheader("Brand revenue")
    brand_data = brand_summary(filtered)
    if not brand_data.empty:
        st.bar_chart(brand_data.set_index("brand")["estimated_monthly_revenue"])
        st.dataframe(brand_data, use_container_width=True, hide_index=True)

with right:
    st.subheader("Price bands")
    price_data = price_band_summary(filtered)
    if not price_data.empty:
        st.bar_chart(price_data.set_index("price_band")["monthly_sales"])
        st.dataframe(price_data, use_container_width=True, hide_index=True)

st.download_button(
    "Download analyzed CSV",
    filtered.to_csv(index=False).encode("utf-8-sig"),
    file_name="market_analysis_result.csv",
    mime="text/csv",
)

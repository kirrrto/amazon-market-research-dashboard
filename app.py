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
from src.finance import ProfitAssumptions, add_profit_estimates

st.set_page_config(page_title="Amazon Market Research Dashboard", layout="wide")

st.title("Amazon Market Research Dashboard")
st.caption("Upload a product research CSV to evaluate demand, competition and market structure.")

sample_path = Path(__file__).parent / "data" / "sample_products.csv"

with st.sidebar:
    st.header("Data source")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    use_sample = st.checkbox("Use included sample data", value=uploaded_file is None)

    st.header("Profit assumptions")
    product_cost = st.number_input(
        "Product cost per unit ($)", min_value=0.0, value=30.0, step=1.0
    )
    shipping_cost = st.number_input(
        "Shipping cost per unit ($)", min_value=0.0, value=8.0, step=1.0
    )
    platform_fee_rate = st.number_input(
        "Platform fee rate (%)", min_value=0.0, max_value=100.0, value=15.0, step=0.5
    )
    advertising_cost_rate = st.number_input(
        "Advertising cost rate (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.5
    )
    return_rate = st.number_input(
        "Return rate (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.5
    )

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

assumptions = ProfitAssumptions(
    product_cost=product_cost,
    shipping_cost=shipping_cost,
    platform_fee_rate=platform_fee_rate / 100,
    advertising_cost_rate=advertising_cost_rate / 100,
    return_rate=return_rate / 100,
)

try:
    filtered = add_profit_estimates(filtered, assumptions)
except ValueError as exc:
    st.error(f"Invalid profit assumptions: {exc}")
    st.stop()

summary = summarize_market(filtered)

metric_1, metric_2, metric_3, metric_4, metric_5 = st.columns(5)
metric_1.metric("Products", f"{summary.product_count}")
metric_2.metric("Average price", f"${summary.average_price:,.2f}")
metric_3.metric("Median reviews", f"{summary.median_reviews:,.0f}")
metric_4.metric("Estimated monthly revenue", f"${summary.estimated_monthly_revenue:,.0f}")
metric_5.metric("Top brand share", f"{summary.top_brand_share:.1%}")

st.subheader("Profit estimation")
total_monthly_net_profit = float(filtered["estimated_monthly_net_profit"].sum())
total_revenue = float(filtered["estimated_monthly_revenue"].sum())
weighted_net_margin = total_monthly_net_profit / total_revenue if total_revenue else 0.0
average_unit_net_profit = (
    float(filtered["estimated_unit_net_profit"].mean()) if not filtered.empty else 0.0
)
break_even_price = (
    float(filtered["break_even_price"].iloc[0]) if not filtered.empty else 0.0
)

profit_1, profit_2, profit_3, profit_4 = st.columns(4)
profit_1.metric("Estimated monthly net profit", f"${total_monthly_net_profit:,.0f}")
profit_2.metric("Weighted net margin", f"{weighted_net_margin:.1%}")
profit_3.metric("Average unit net profit", f"${average_unit_net_profit:,.2f}")
profit_4.metric("Break-even price", f"${break_even_price:,.2f}")
st.caption(
    "Profit estimates use the same cost assumptions for every product and are intended "
    "for early-stage screening rather than final accounting."
)

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
            "estimated_unit_net_profit",
            "estimated_net_margin",
            "estimated_monthly_net_profit",
            "opportunity_score",
        ]
    ],
    use_container_width=True,
    hide_index=True,
    column_config={
        "estimated_net_margin": st.column_config.NumberColumn(
            "Estimated net margin", format="percent"
        ),
    },
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

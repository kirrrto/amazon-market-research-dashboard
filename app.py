from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import streamlit as st

from src.analysis import brand_summary, price_band_summary, summarize_market
from src.finance import ProfitAssumptions, add_profit_estimates
from src.importers.export import (
    build_normalized_workbook,
    prepare_export_result,
)
from src.importers.mapping import (
    FIELD_LABELS,
    STANDARD_FIELDS,
    FieldMappingError,
    apply_field_mapping,
    suggest_field_mappings,
    validate_field_mapping,
)
from src.importers.tabular import (
    TabularImportError,
    list_worksheets,
    read_tabular_file,
)
from src.importers.validation import validate_and_clean_import


st.set_page_config(
    page_title="Amazon Market Research Dashboard",
    layout="wide",
)
st.title("Amazon Market Research Dashboard")
st.caption(
    "Import product research spreadsheets, standardize fields, validate data "
    "and evaluate market and profit opportunities."
)

sample_path = Path(__file__).parent / "data" / "sample_products.csv"
NOT_MAPPED = "— Not mapped —"

with st.sidebar:
    st.header("Data source")
    uploaded_file = st.file_uploader(
        "Upload CSV or Excel",
        type=["csv", "xlsx", "xls"],
        help="Supported formats: CSV, XLSX and XLS. Project limit: 20 MB.",
    )
    use_sample = st.checkbox(
        "Use included sample data",
        value=uploaded_file is None,
    )

    st.header("Profit assumptions")
    product_cost = st.number_input(
        "Product cost per unit ($)",
        min_value=0.0,
        value=30.0,
        step=1.0,
    )
    shipping_cost = st.number_input(
        "Shipping cost per unit ($)",
        min_value=0.0,
        value=8.0,
        step=1.0,
    )
    platform_fee_rate = st.number_input(
        "Platform fee rate (%)",
        min_value=0.0,
        max_value=100.0,
        value=15.0,
        step=0.5,
    )
    advertising_cost_rate = st.number_input(
        "Advertising cost rate (%)",
        min_value=0.0,
        max_value=100.0,
        value=10.0,
        step=0.5,
    )
    return_rate = st.number_input(
        "Return rate (%)",
        min_value=0.0,
        max_value=100.0,
        value=5.0,
        step=0.5,
    )

if uploaded_file is not None:
    file_name = uploaded_file.name
    file_content = uploaded_file.getvalue()
elif use_sample:
    file_name = sample_path.name
    file_content = sample_path.read_bytes()
else:
    st.info("Upload a spreadsheet or enable the included sample data.")
    st.stop()

worksheet: str | None = None
st.subheader("Step 1 — Select source data")
try:
    sheets = list_worksheets(file_name, file_content)
    if sheets:
        worksheet = st.selectbox("Worksheet", sheets)
    else:
        st.caption("CSV and sample files do not require worksheet selection.")
    raw_data = read_tabular_file(file_name, file_content, worksheet)
except TabularImportError as exc:
    st.error(f"Unable to import file: {exc}")
    st.stop()

st.subheader("Step 2 — Preview source data")
preview_1, preview_2 = st.columns(2)
preview_1.metric("Rows", f"{len(raw_data):,}")
preview_2.metric("Columns", f"{len(raw_data.columns):,}")
st.dataframe(raw_data.head(20), use_container_width=True, hide_index=True)

st.subheader("Step 3 — Confirm field mapping")
suggestions = suggest_field_mappings(raw_data.columns)
options = [NOT_MAPPED, *[str(column) for column in raw_data.columns]]
mapping: dict[str, str | None] = {}

mapping_columns = st.columns(2)
for index, standard_field in enumerate(STANDARD_FIELDS):
    suggestion = suggestions.get(standard_field)
    default_index = options.index(suggestion) if suggestion in options else 0
    with mapping_columns[index % 2]:
        selected = st.selectbox(
            FIELD_LABELS[standard_field],
            options,
            index=default_index,
            key=f"mapping::{file_name}::{worksheet}::{standard_field}",
        )
    mapping[standard_field] = None if selected == NOT_MAPPED else selected

mapping_error: str | None = None
try:
    validate_field_mapping(mapping, raw_data.columns)
except FieldMappingError as exc:
    mapping_error = str(exc)
    st.warning(mapping_error)

signature_payload = repr(
    (file_name, worksheet, sorted(mapping.items()))
).encode("utf-8")
import_signature = hashlib.sha256(signature_payload).hexdigest()

if st.session_state.get("import_signature") != import_signature:
    st.session_state.pop("import_result", None)
    st.session_state["import_signature"] = import_signature

if st.button(
    "Validate and import",
    type="primary",
    disabled=mapping_error is not None,
):
    try:
        mapped_data = apply_field_mapping(raw_data, mapping)
        st.session_state["import_result"] = validate_and_clean_import(
            mapped_data,
            source_file=file_name,
            worksheet=worksheet,
            mapping={
                field: str(source)
                for field, source in mapping.items()
                if source is not None
            },
        )
    except (FieldMappingError, ValueError) as exc:
        st.error(f"Import validation failed: {exc}")

result = st.session_state.get("import_result")
if result is None:
    st.info("Confirm the mappings and select “Validate and import” to continue.")
    st.stop()

st.subheader("Step 4 — Import validation")
report = result.report
report_columns = st.columns(5)
report_columns[0].metric("Original rows", f"{report.original_rows:,}")
report_columns[1].metric("Valid rows", f"{report.valid_rows:,}")
report_columns[2].metric("Rejected rows", f"{report.rejected_rows:,}")
report_columns[3].metric("Warning rows", f"{report.warning_rows:,}")
report_columns[4].metric("Duplicate ASINs", f"{report.duplicate_asins:,}")

if result.issues:
    st.dataframe(
        result.issues_frame,
        use_container_width=True,
        hide_index=True,
    )
else:
    st.success("No import issues were detected.")

if result.products.empty:
    st.error("No valid product rows remain. Correct the source file and retry.")
    st.stop()

assumptions = ProfitAssumptions(
    product_cost=product_cost,
    shipping_cost=shipping_cost,
    platform_fee_rate=platform_fee_rate / 100,
    advertising_cost_rate=advertising_cost_rate / 100,
    return_rate=return_rate / 100,
)

try:
    export_result = prepare_export_result(result, assumptions)
except ValueError as exc:
    st.error(f"Invalid profit assumptions: {exc}")
    st.stop()

workbook_bytes = build_normalized_workbook(export_result)
st.download_button(
    "Download normalized workbook",
    data=workbook_bytes,
    file_name="normalized_products.xlsx",
    mime=(
        "application/vnd.openxmlformats-officedocument."
        "spreadsheetml.sheet"
    ),
)

data = export_result.products.copy()
categories = sorted(data["category"].dropna().unique().tolist())
brands = sorted(data["brand"].dropna().unique().tolist())

with st.sidebar:
    selected_categories = st.multiselect(
        "Categories",
        categories,
        default=categories,
    )
    selected_brands = st.multiselect(
        "Brands",
        brands,
        default=brands,
    )

filtered = data[
    data["category"].isin(selected_categories)
    & data["brand"].isin(selected_brands)
].copy()

st.subheader("Step 5 — Market and profit analysis")
summary = summarize_market(filtered)

metric_1, metric_2, metric_3, metric_4, metric_5 = st.columns(5)
metric_1.metric("Products", f"{summary.product_count}")
metric_2.metric("Average price", f"${summary.average_price:,.2f}")
metric_3.metric("Median reviews", f"{summary.median_reviews:,.0f}")
metric_4.metric(
    "Estimated monthly revenue",
    f"${summary.estimated_monthly_revenue:,.0f}",
)
metric_5.metric("Top brand share", f"{summary.top_brand_share:.1%}")

total_monthly_net_profit = float(
    filtered["estimated_monthly_net_profit"].sum()
)
total_revenue = float(filtered["estimated_monthly_revenue"].sum())
weighted_net_margin = (
    total_monthly_net_profit / total_revenue if total_revenue else 0.0
)
average_unit_net_profit = (
    float(filtered["estimated_unit_net_profit"].mean())
    if not filtered.empty
    else 0.0
)
break_even_price = (
    float(filtered["break_even_price"].iloc[0])
    if not filtered.empty
    else 0.0
)

profit_1, profit_2, profit_3, profit_4 = st.columns(4)
profit_1.metric(
    "Estimated monthly net profit",
    f"${total_monthly_net_profit:,.0f}",
)
profit_2.metric("Weighted net margin", f"{weighted_net_margin:.1%}")
profit_3.metric(
    "Average unit net profit",
    f"${average_unit_net_profit:,.2f}",
)
profit_4.metric("Break-even price", f"${break_even_price:,.2f}")

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
            "Estimated net margin",
            format="percent",
        ),
    },
)

left, right = st.columns(2)
with left:
    st.subheader("Brand revenue")
    brand_data = brand_summary(filtered)
    if not brand_data.empty:
        st.bar_chart(
            brand_data.set_index("brand")[
                "estimated_monthly_revenue"
            ]
        )
        st.dataframe(
            brand_data,
            use_container_width=True,
            hide_index=True,
        )

with right:
    st.subheader("Price bands")
    price_data = price_band_summary(filtered)
    if not price_data.empty:
        st.bar_chart(
            price_data.set_index("price_band")["monthly_sales"]
        )
        st.dataframe(
            price_data,
            use_container_width=True,
            hide_index=True,
        )

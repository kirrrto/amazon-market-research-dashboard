from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import streamlit as st

from src.analysis import brand_summary, price_band_summary, summarize_market
from src.connectors.export import (
    build_product_page_workbook,
    coverage_summary_frame,
    gap_analysis_frame,
    normalized_specs_frame,
    specification_matrix_frame,
)
from src.connectors.product_page import collect_product_pages
from src.finance import ProfitAssumptions
from src.i18n import (
    LANGUAGE_DISPLAY_NAMES,
    SUPPORTED_LANGUAGES,
    column_label,
    normalize_language,
    t,
)
from src.importers.export import (
    build_normalized_workbook,
    prepare_export_result,
)
from src.importers.mapping import (
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
from src.specs import list_spec_profiles
from src.templates import build_template_workbook, list_template_definitions


st.set_page_config(
    page_title="Amazon Market Research Dashboard",
    layout="wide",
)

sample_path = Path(__file__).parent / "data" / "sample_products.csv"

DISPLAY_TO_LANGUAGE = {
    LANGUAGE_DISPLAY_NAMES[code]: code for code in SUPPORTED_LANGUAGES
}


def _language_select(label: str, default: str = "en") -> str:
    default_code = normalize_language(default)
    options = [LANGUAGE_DISPLAY_NAMES[code] for code in SUPPORTED_LANGUAGES]
    selected = st.selectbox(
        label,
        options,
        index=list(SUPPORTED_LANGUAGES).index(default_code),
    )
    return DISPLAY_TO_LANGUAGE[selected]


with st.sidebar:
    language = _language_select("Language / 语言", "en")
    export_language = _language_select(t("export_language", language), language)

st.title(t("app_title", language))
st.caption(t("app_caption", language))


def _localized_frame(frame: pd.DataFrame, language: str) -> pd.DataFrame:
    return frame.rename(columns={column: column_label(str(column), language) for column in frame.columns})


def _parse_url_lines(value: str) -> list[str]:
    return [line.strip() for line in value.splitlines() if line.strip()]


def _show_template_center(language: str) -> None:
    st.subheader(t("template_center", language))
    st.caption(t("template_center_intro", language))

    button_keys = {
        "market_research": "download_market_research_template",
        "supplier_quote": "download_supplier_quote_template",
        "product_url_import": "download_product_url_template",
        "security_camera_specs": "download_security_camera_template",
        "vehicle_camera_specs": "download_vehicle_camera_template",
    }

    for definition in list_template_definitions():
        with st.container(border=True):
            st.markdown(f"### {definition.title(language)}")
            st.write(definition.description(language))
            st.download_button(
                t(button_keys[definition.template_id], language),
                data=build_template_workbook(definition.template_id, language),
                file_name=definition.file_name,
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
                key=f"template::{definition.template_id}::{language}",
            )


with st.sidebar:
    st.header(t("data_source", language))

    mode_labels = {
        "sample": t("use_sample_data", language),
        "spreadsheet": t("upload_csv_excel", language),
        "urls": t("import_from_product_urls", language),
        "templates": t("template_center", language),
    }
    selected_mode_label = st.radio(
        t("input_mode", language),
        list(mode_labels.values()),
        index=0,
    )
    data_source_mode = {
        value: key for key, value in mode_labels.items()
    }[selected_mode_label]

    uploaded_file = None
    if data_source_mode == "spreadsheet":
        uploaded_file = st.file_uploader(
            t("upload_csv_excel", language),
            type=["csv", "xlsx", "xls"],
            help="CSV, XLSX, XLS. 20MB per file.",
        )
    elif data_source_mode == "urls":
        st.caption(
            "Use public supplier or brand product pages. Do not use login-only, "
            "CAPTCHA-protected or restricted pages."
            if language == "en"
            else "请使用公开供应商或品牌产品页面。不要使用登录、验证码保护或受限页面。"
        )

    if data_source_mode in {"sample", "spreadsheet"}:
        st.header(t("profit_assumptions", language))
        product_cost = st.number_input(
            t("product_cost_per_unit", language),
            min_value=0.0,
            value=30.0,
            step=1.0,
        )
        shipping_cost = st.number_input(
            t("shipping_cost_per_unit", language),
            min_value=0.0,
            value=8.0,
            step=1.0,
        )
        platform_fee_rate = st.number_input(
            t("platform_fee_rate", language),
            min_value=0.0,
            max_value=100.0,
            value=15.0,
            step=0.5,
        )
        advertising_cost_rate = st.number_input(
            t("advertising_cost_rate", language),
            min_value=0.0,
            max_value=100.0,
            value=10.0,
            step=0.5,
        )
        return_rate = st.number_input(
            t("return_rate", language),
            min_value=0.0,
            max_value=100.0,
            value=5.0,
            step=0.5,
        )


if data_source_mode == "templates":
    _show_template_center(language)
    st.stop()


if data_source_mode == "urls":
    st.subheader(t("product_page_connector", language))
    st.caption(t("product_page_connector_caption", language))
    st.warning(t("connector_scope_warning", language), icon="⚠️")

    profile_options = {
        profile.label(language): profile.profile_id
        for profile in list_spec_profiles()
    }
    selected_profile_label = st.selectbox(
        "Spec profile" if language == "en" else "规格配置模板",
        list(profile_options.keys()),
        index=0,
    )
    selected_profile = profile_options[selected_profile_label]

    url_text = st.text_area(
        t("product_page_urls", language),
        height=180,
        placeholder=(
            "https://supplier.example.com/product/wireless-backup-camera\n"
            "https://brand.example.com/products/4g-solar-camera"
        ),
    )
    urls = _parse_url_lines(url_text)

    if st.button(t("fetch_product_pages", language), type="primary"):
        if not urls:
            st.error(
                "Paste at least one product page URL."
                if language == "en"
                else "请至少粘贴一个产品页面 URL。"
            )
        else:
            spinner_text = (
                f"Fetching {len(urls)} URL(s)..."
                if language == "en"
                else f"正在抓取 {len(urls)} 个 URL..."
            )
            with st.spinner(spinner_text):
                st.session_state["product_page_connector_result"] = collect_product_pages(urls)

    connector_result = st.session_state.get("product_page_connector_result")
    if connector_result is None:
        st.info(
            "Paste URLs and select “Fetch product pages” to start collection."
            if language == "en"
            else "粘贴 URL 后点击“抓取产品页面”开始采集。"
        )
        st.stop()

    products_frame = connector_result.products_frame
    specs_frame = connector_result.raw_specs_frame
    normalized_frame = normalized_specs_frame(connector_result, language)
    matrix_frame = specification_matrix_frame(connector_result, language)
    coverage_frame = coverage_summary_frame(connector_result, language)
    gaps_frame = gap_analysis_frame(
        connector_result,
        profile=selected_profile,
        language=language,
    )
    logs_frame = connector_result.fetch_logs_frame
    issues_frame = connector_result.issues_frame

    st.subheader(t("connector_results", language))
    metric_1, metric_2, metric_3, metric_4 = st.columns(4)
    metric_1.metric(t("products", language), f"{len(products_frame):,}")
    metric_2.metric(
        t("successful_fetches", language),
        f"{int(logs_frame['success'].sum()) if not logs_frame.empty else 0:,}",
    )
    metric_3.metric(t("raw_specs", language), f"{len(specs_frame):,}")
    metric_4.metric(t("issues", language), f"{len(issues_frame):,}")

    tab_products, tab_specs, tab_normalized, tab_matrix, tab_coverage, tab_gaps, tab_logs, tab_issues = st.tabs(
        [
            t("products", language),
            t("raw_specifications", language),
            t("normalized_specifications", language),
            t("specification_matrix", language),
            t("coverage_summary", language),
            t("gap_analysis", language),
            t("fetch_logs", language),
            t("issues", language),
        ]
    )
    with tab_products:
        st.dataframe(_localized_frame(products_frame, language), use_container_width=True, hide_index=True)
    with tab_specs:
        st.dataframe(_localized_frame(specs_frame, language), use_container_width=True, hide_index=True)
    with tab_normalized:
        st.dataframe(_localized_frame(normalized_frame, language), use_container_width=True, hide_index=True)
    with tab_matrix:
        st.dataframe(_localized_frame(matrix_frame, language), use_container_width=True, hide_index=True)
    with tab_coverage:
        coverage_display = _localized_frame(coverage_frame, language)
        st.dataframe(
            coverage_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                column_label("coverage_rate", language): st.column_config.NumberColumn(
                    column_label("coverage_rate", language),
                    format="percent",
                ),
            },
        )
    with tab_gaps:
        gaps_display = _localized_frame(gaps_frame, language)
        st.dataframe(
            gaps_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                column_label("completion_rate", language): st.column_config.NumberColumn(
                    column_label("completion_rate", language),
                    format="percent",
                ),
            },
        )
    with tab_logs:
        st.dataframe(_localized_frame(logs_frame, language), use_container_width=True, hide_index=True)
    with tab_issues:
        if issues_frame.empty:
            st.success(
                "No connector issues were recorded."
                if language == "en"
                else "未记录连接器问题。"
            )
        else:
            st.dataframe(_localized_frame(issues_frame, language), use_container_width=True, hide_index=True)

    st.download_button(
        t("download_product_page_workbook", language),
        data=build_product_page_workbook(
            connector_result,
            language=export_language,
            profile=selected_profile,
        ),
        file_name="product_page_import.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )
    st.stop()


if data_source_mode == "spreadsheet":
    if uploaded_file is None:
        st.info("Upload a spreadsheet to continue." if language == "en" else "请上传表格文件继续。")
        st.stop()
    file_name = uploaded_file.name
    file_content = uploaded_file.getvalue()
else:
    file_name = sample_path.name
    file_content = sample_path.read_bytes()

worksheet: str | None = None
st.subheader(t("step_select_source", language))
try:
    sheets = list_worksheets(file_name, file_content)
    if sheets:
        worksheet = st.selectbox(t("worksheet", language), sheets)
    else:
        st.caption(
            "CSV and sample files do not require worksheet selection."
            if language == "en"
            else "CSV 和示例文件不需要选择工作表。"
        )
    raw_data = read_tabular_file(file_name, file_content, worksheet)
except TabularImportError as exc:
    st.error(f"Unable to import file: {exc}" if language == "en" else f"无法导入文件：{exc}")
    st.stop()

st.subheader(t("step_preview_data", language))
preview_1, preview_2 = st.columns(2)
preview_1.metric(t("rows", language), f"{len(raw_data):,}")
preview_2.metric(t("columns", language), f"{len(raw_data.columns):,}")
st.dataframe(raw_data.head(20), use_container_width=True, hide_index=True)

st.subheader(t("step_confirm_mapping", language))
suggestions = suggest_field_mappings(raw_data.columns)
not_mapped = t("not_mapped", language)
options = [not_mapped, *[str(column) for column in raw_data.columns]]
mapping: dict[str, str | None] = {}

mapping_columns = st.columns(2)
for index, standard_field in enumerate(STANDARD_FIELDS):
    suggestion = suggestions.get(standard_field)
    default_index = options.index(suggestion) if suggestion in options else 0
    with mapping_columns[index % 2]:
        selected = st.selectbox(
            column_label(standard_field, language),
            options,
            index=default_index,
            key=f"mapping::{file_name}::{worksheet}::{standard_field}::{language}",
        )
    mapping[standard_field] = None if selected == not_mapped else selected

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
    t("validate_and_import", language),
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
        st.error(f"Import validation failed: {exc}" if language == "en" else f"导入校验失败：{exc}")

result = st.session_state.get("import_result")
if result is None:
    st.info(
        "Confirm the mappings and select “Validate and import” to continue."
        if language == "en"
        else "确认字段映射后，点击“校验并导入”继续。"
    )
    st.stop()

st.subheader(t("step_import_validation", language))
report = result.report
report_columns = st.columns(5)
report_columns[0].metric(t("original_rows", language), f"{report.original_rows:,}")
report_columns[1].metric(t("valid_rows", language), f"{report.valid_rows:,}")
report_columns[2].metric(t("rejected_rows", language), f"{report.rejected_rows:,}")
report_columns[3].metric(t("warning_rows", language), f"{report.warning_rows:,}")
report_columns[4].metric(t("duplicate_asins", language), f"{report.duplicate_asins:,}")

if result.issues:
    st.dataframe(
        _localized_frame(result.issues_frame, language),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.success(t("no_import_issues", language))

if result.products.empty:
    st.error("No valid product rows remain. Correct the source file and retry." if language == "en" else "没有可用产品行。请修正源文件后重试。")
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
    st.error(f"Invalid profit assumptions: {exc}" if language == "en" else f"利润参数无效：{exc}")
    st.stop()

workbook_bytes = build_normalized_workbook(export_result, language=export_language)
st.download_button(
    t("download_normalized_workbook", language),
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
        t("category_filter", language),
        categories,
        default=categories,
    )
    selected_brands = st.multiselect(
        t("brand_filter", language),
        brands,
        default=brands,
    )

filtered = data[
    data["category"].isin(selected_categories)
    & data["brand"].isin(selected_brands)
].copy()

st.subheader(t("step_market_profit", language))
summary = summarize_market(filtered)

metric_1, metric_2, metric_3, metric_4, metric_5 = st.columns(5)
metric_1.metric(t("products", language), f"{summary.product_count}")
metric_2.metric(t("average_price", language), f"${summary.average_price:,.2f}")
metric_3.metric(t("median_reviews", language), f"{summary.median_reviews:,.0f}")
metric_4.metric(
    t("estimated_monthly_revenue", language),
    f"${summary.estimated_monthly_revenue:,.0f}",
)
metric_5.metric(t("top_brand_share", language), f"{summary.top_brand_share:.1%}")

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
    t("estimated_monthly_net_profit", language),
    f"${total_monthly_net_profit:,.0f}",
)
profit_2.metric(t("weighted_net_margin", language), f"{weighted_net_margin:.1%}")
profit_3.metric(
    t("average_unit_net_profit", language),
    f"${average_unit_net_profit:,.2f}",
)
profit_4.metric(t("break_even_price", language), f"${break_even_price:,.2f}")

st.subheader(t("highest_opportunity_products", language))
opportunities = filtered.sort_values(
    ["opportunity_score", "estimated_monthly_revenue"],
    ascending=False,
)
opportunity_columns = [
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
opportunity_frame = opportunities[opportunity_columns].rename(
    columns={column: column_label(column, language) for column in opportunity_columns}
)
net_margin_label = column_label("estimated_net_margin", language)
st.dataframe(
    opportunity_frame,
    use_container_width=True,
    hide_index=True,
    column_config={
        net_margin_label: st.column_config.NumberColumn(
            net_margin_label,
            format="percent",
        ),
    },
)

left, right = st.columns(2)
with left:
    st.subheader(t("brand_revenue", language))
    brand_data = brand_summary(filtered)
    if not brand_data.empty:
        st.bar_chart(
            brand_data.set_index("brand")[
                "estimated_monthly_revenue"
            ]
        )
        st.dataframe(
            _localized_frame(brand_data, language),
            use_container_width=True,
            hide_index=True,
        )

with right:
    st.subheader(t("price_bands", language))
    price_data = price_band_summary(filtered)
    if not price_data.empty:
        st.bar_chart(
            price_data.set_index("price_band")["monthly_sales"]
        )
        st.dataframe(
            _localized_frame(price_data, language),
            use_container_width=True,
            hide_index=True,
        )

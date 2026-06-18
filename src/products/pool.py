from __future__ import annotations

from collections import Counter
from typing import Any
from urllib.parse import urlparse

import pandas as pd

from src.suppliers import supplier_group_key


PRODUCT_POOL_COLUMNS = [
    "source_url",
    "title",
    "brand",
    "model",
    "supplier_key",
    "supplier_name",
    "domain",
    "readiness_score",
    "readiness_status",
    "product_pool_status",
    "priority",
    "risk_level",
    "completion_rate",
    "metadata_completeness",
    "missing_count",
    "required_fields_count",
    "follow_up_question_count",
    "requirement_candidate_count",
    "supplier_average_readiness_score",
    "supplier_overall_status",
    "recommendation",
    "next_action",
    "missing_fields",
    "missing_labels",
]

POOL_STATUS_LABELS = {
    "en": {
        "review": "Review Candidate",
        "follow_up": "Supplier Follow-up",
        "risk_review": "Risk Review",
        "hold": "Hold",
    },
    "zh-CN": {
        "review": "评审候选",
        "follow_up": "供应商追问",
        "risk_review": "风险复核",
        "hold": "暂缓",
    },
}

PRIORITY_LABELS = {
    "en": {
        "p1": "P1",
        "p2": "P2",
        "p3": "P3",
        "p4": "P4",
    },
    "zh-CN": {
        "p1": "P1",
        "p2": "P2",
        "p3": "P3",
        "p4": "P4",
    },
}

RECOMMENDATIONS = {
    "en": {
        "review": "Move this product into product review and compare cost, compliance and engineering assumptions.",
        "follow_up": "Keep this product in the pool and request missing information from the supplier.",
        "risk_review": "Review the risk before assigning engineering or sourcing resources.",
        "hold": "Keep as a low-priority reference until core product data is improved.",
    },
    "zh-CN": {
        "review": "进入产品评审，并继续对比成本、认证和研发可行性。",
        "follow_up": "保留在产品池中，并向供应商补充确认缺失信息。",
        "risk_review": "分配研发或采购资源前，先复核风险点。",
        "hold": "作为低优先级参考保留，待核心资料补齐后再推进。",
    },
}

NEXT_ACTIONS = {
    "en": {
        "review": "Prepare requirement review inputs and supplier quote comparison.",
        "follow_up": "Send supplier follow-up questions and update the product pool after response.",
        "risk_review": "Resolve missing required fields and confirm technical feasibility.",
        "hold": "Collect basic metadata, required specifications and supplier documents.",
    },
    "zh-CN": {
        "review": "准备需求评审输入和供应商报价对比。",
        "follow_up": "发送供应商追问清单，收到回复后更新产品池。",
        "risk_review": "解决缺失必需字段，并确认技术可行性。",
        "hold": "先补齐基础信息、必需规格和供应商资料。",
    },
}


def _language(language: str = "en") -> str:
    return "zh-CN" if language == "zh-CN" else "en"


def _records(value: pd.DataFrame | list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    if value is None:
        return []
    if isinstance(value, pd.DataFrame):
        return value.to_dict("records")
    return list(value or [])


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    try:
        if pd.isna(value):
            return True
    except (TypeError, ValueError):
        pass
    return str(value).strip() == ""


def _as_float(value: Any, default: float = 0.0) -> float:
    if _is_missing(value):
        return default
    try:
        number = float(str(value).replace("%", "").strip())
    except ValueError:
        return default
    return number


def _as_int(value: Any, default: int = 0) -> int:
    if _is_missing(value):
        return default
    try:
        return int(float(str(value).replace("%", "").strip()))
    except ValueError:
        return default


def _domain_from_url(url: Any) -> str:
    text = str(url or "").strip()
    if not text:
        return ""
    parsed = urlparse(text if "://" in text else f"https://{text}")
    return parsed.netloc.lower().removeprefix("www.")


def _supplier_name(row: dict[str, Any]) -> str:
    brand = str(row.get("brand", "") or "").strip()
    if brand:
        return brand

    domain = _domain_from_url(row.get("source_url", ""))
    return domain or "Unknown Supplier"


def _status_key(score: float, risk_level: str, readiness_status: Any = "") -> str:
    risk = str(risk_level or "").strip().lower()
    status = str(readiness_status or "").strip().lower()

    if score >= 80 and risk == "low":
        return "review"
    if score >= 60 and risk != "high":
        return "follow_up"
    if score >= 40 or risk == "high" or "risk" in status or "风险" in status:
        return "risk_review"
    return "hold"


def _priority_key(status_key: str) -> str:
    return {
        "review": "p1",
        "follow_up": "p2",
        "risk_review": "p3",
        "hold": "p4",
    }[status_key]


def _priority_rank(priority: str) -> int:
    return {
        "P1": 1,
        "P2": 2,
        "P3": 3,
        "P4": 4,
    }.get(str(priority or ""), 9)


def product_pool_status_for_readiness(
    readiness_score: float,
    risk_level: str,
    readiness_status: str = "",
    language: str = "en",
) -> str:
    """Return the product pool status label for a product candidate."""

    key = _status_key(float(readiness_score), risk_level, readiness_status)
    return POOL_STATUS_LABELS[_language(language)][key]


def _source_url_counts(
    rows: list[dict[str, Any]],
    *,
    non_empty_field: str | None = None,
) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in rows:
        source_url = str(row.get("source_url", "") or "").strip()
        if not source_url:
            continue
        if non_empty_field and _is_missing(row.get(non_empty_field)):
            continue
        counts[source_url] += 1
    return counts


def _supplier_lookup(
    supplier_comparison: pd.DataFrame | list[dict[str, Any]] | None,
) -> dict[str, dict[str, Any]]:
    lookup: dict[str, dict[str, Any]] = {}
    for row in _records(supplier_comparison):
        supplier_key = str(row.get("supplier_key", "") or "").strip()
        if supplier_key:
            lookup[supplier_key] = row
    return lookup


def build_product_pool_summary(
    product_readiness: pd.DataFrame | list[dict[str, Any]],
    *,
    supplier_comparison: pd.DataFrame | list[dict[str, Any]] | None = None,
    supplier_follow_up: pd.DataFrame | list[dict[str, Any]] | None = None,
    requirement_draft: pd.DataFrame | list[dict[str, Any]] | None = None,
    language: str = "en",
) -> pd.DataFrame:
    """Build a product pool summary from readiness and supplier comparison data.

    Product pool rows are intended for filtering, prioritization and review.
    They preserve product-level readiness while adding supplier-level context.
    """

    product_rows = _records(product_readiness)
    if not product_rows:
        return pd.DataFrame(columns=PRODUCT_POOL_COLUMNS)

    follow_up_counts = _source_url_counts(_records(supplier_follow_up))
    requirement_counts = _source_url_counts(
        _records(requirement_draft),
        non_empty_field="current_value",
    )
    suppliers = _supplier_lookup(supplier_comparison)

    output_rows: list[dict[str, Any]] = []
    lang = _language(language)

    for row in product_rows:
        supplier_key = supplier_group_key(row)
        supplier_row = suppliers.get(supplier_key, {})
        score = round(_as_float(row.get("readiness_score")), 2)
        risk_level = str(row.get("risk_level", "") or "unknown").strip().lower()
        readiness_status = str(row.get("readiness_status", "") or "")
        status_key = _status_key(score, risk_level, readiness_status)
        priority_key = _priority_key(status_key)
        source_url = str(row.get("source_url", "") or "").strip()

        output_rows.append(
            {
                "source_url": source_url,
                "title": str(row.get("title", "") or ""),
                "brand": str(row.get("brand", "") or ""),
                "model": str(row.get("model", "") or ""),
                "supplier_key": supplier_key,
                "supplier_name": str(supplier_row.get("supplier_name", "") or _supplier_name(row)),
                "domain": str(supplier_row.get("domain", "") or _domain_from_url(source_url)),
                "readiness_score": score,
                "readiness_status": readiness_status,
                "product_pool_status": POOL_STATUS_LABELS[lang][status_key],
                "priority": PRIORITY_LABELS[lang][priority_key],
                "risk_level": risk_level,
                "completion_rate": round(_as_float(row.get("completion_rate")), 4),
                "metadata_completeness": round(_as_float(row.get("metadata_completeness")), 4),
                "missing_count": _as_int(row.get("missing_count")),
                "required_fields_count": _as_int(row.get("required_fields_count")),
                "follow_up_question_count": _as_int(
                    row.get("follow_up_question_count"),
                    default=follow_up_counts[source_url],
                ),
                "requirement_candidate_count": _as_int(
                    row.get("requirement_candidate_count"),
                    default=requirement_counts[source_url],
                ),
                "supplier_average_readiness_score": round(
                    _as_float(supplier_row.get("average_readiness_score")),
                    2,
                ),
                "supplier_overall_status": str(supplier_row.get("overall_status", "") or ""),
                "recommendation": RECOMMENDATIONS[lang][status_key],
                "next_action": NEXT_ACTIONS[lang][status_key],
                "missing_fields": str(row.get("missing_fields", "") or ""),
                "missing_labels": str(row.get("missing_labels", "") or ""),
            }
        )

    frame = pd.DataFrame(output_rows, columns=PRODUCT_POOL_COLUMNS)
    frame["_priority_rank"] = frame["priority"].map(_priority_rank)
    frame = frame.sort_values(
        by=["_priority_rank", "readiness_score", "completion_rate"],
        ascending=[True, False, False],
        ignore_index=True,
    )
    return frame.drop(columns=["_priority_rank"])

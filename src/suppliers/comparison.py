from __future__ import annotations

from collections import Counter, defaultdict
from statistics import mean
from typing import Any
from urllib.parse import urlparse

import pandas as pd


SUPPLIER_COMPARISON_COLUMNS = [
    "supplier_key",
    "supplier_name",
    "domain",
    "product_count",
    "average_readiness_score",
    "max_readiness_score",
    "average_completion_rate",
    "ready_product_count",
    "follow_up_required_count",
    "high_risk_product_count",
    "not_ready_product_count",
    "total_missing_fields",
    "total_follow_up_questions",
    "requirement_candidate_count",
    "best_product_title",
    "best_product_url",
    "overall_status",
    "recommendation",
    "next_action",
]


STATUS_LABELS = {
    "en": {
        "strong": "Strong Candidate",
        "follow_up": "Needs Follow-up",
        "high_risk": "High Risk",
        "not_ready": "Not Ready",
    },
    "zh-CN": {
        "strong": "强候选供应商",
        "follow_up": "需要补充确认",
        "high_risk": "高风险",
        "not_ready": "暂不建议继续",
    },
}

RECOMMENDATIONS = {
    "en": {
        "strong": "Prioritize this supplier for product review and commercial negotiation.",
        "follow_up": "Continue supplier follow-up before committing product resources.",
        "high_risk": "Treat as a risky supplier candidate until key gaps are resolved.",
        "not_ready": "Do not prioritize this supplier until product data quality improves.",
    },
    "zh-CN": {
        "strong": "优先进入产品评审和商务沟通。",
        "follow_up": "在投入产品资源前，继续向供应商补充确认。",
        "high_risk": "关键缺口解决前，作为高风险供应商候选处理。",
        "not_ready": "产品资料质量改善前，不建议优先推进。",
    },
}

NEXT_ACTIONS = {
    "en": {
        "strong": "Compare quote, MOQ, lead time, compliance documents and engineering feasibility.",
        "follow_up": "Send supplier questions and update readiness score after response.",
        "high_risk": "Resolve missing specifications and supplier data gaps before review.",
        "not_ready": "Collect complete product metadata and required specifications first.",
    },
    "zh-CN": {
        "strong": "继续对比报价、MOQ、交期、认证文件和研发可行性。",
        "follow_up": "发送供应商追问清单，收到回复后重新评分。",
        "high_risk": "产品评审前先解决缺失规格和供应商资料缺口。",
        "not_ready": "先补齐产品基础信息和必需规格。",
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
        return float(str(value).replace("%", "").strip())
    except ValueError:
        return default


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


def supplier_group_key(row: dict[str, Any]) -> str:
    """Return a stable supplier grouping key.

    Brand is used when available because supplier product pages often contain
    multiple domains or CDN paths. Domain is used as the fallback.
    """

    brand = str(row.get("brand", "") or "").strip()
    if brand:
        return brand.lower()

    domain = _domain_from_url(row.get("source_url", ""))
    if domain:
        return domain

    return "unknown_supplier"


def _supplier_name(row: dict[str, Any]) -> str:
    brand = str(row.get("brand", "") or "").strip()
    if brand:
        return brand

    domain = _domain_from_url(row.get("source_url", ""))
    return domain or "Unknown Supplier"


def _source_url_counts(records: list[dict[str, Any]], field_name: str | None = None) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in records:
        source_url = str(row.get("source_url", "") or "").strip()
        if not source_url:
            continue
        if field_name and _is_missing(row.get(field_name)):
            continue
        counts[source_url] += 1
    return counts


def _status_key(
    average_score: float,
    high_risk_count: int,
    not_ready_count: int,
) -> str:
    if average_score >= 80 and high_risk_count == 0 and not_ready_count == 0:
        return "strong"
    if average_score >= 60 and not_ready_count == 0:
        return "follow_up"
    if average_score >= 40:
        return "high_risk"
    return "not_ready"


def supplier_status_for_score(
    average_score: float,
    *,
    high_risk_count: int = 0,
    not_ready_count: int = 0,
    language: str = "en",
) -> str:
    """Return a supplier-level status label from aggregate product readiness."""

    key = _status_key(average_score, high_risk_count, not_ready_count)
    return STATUS_LABELS[_language(language)][key]


def _status_bucket(readiness_status: Any) -> str:
    text = str(readiness_status or "").strip().lower()

    if text in {"ready for review", "可以进入评审"}:
        return "ready"
    if text in {"follow-up required", "follow up required", "需要补充确认"}:
        return "follow_up"
    if text in {"high risk", "高风险"}:
        return "high_risk"
    if text in {"not ready", "暂不建议继续"}:
        return "not_ready"

    if "ready" in text and "not" not in text:
        return "ready"
    if "follow" in text or "补充" in text:
        return "follow_up"
    if "risk" in text or "风险" in text:
        return "high_risk"
    return "not_ready"


def build_supplier_comparison(
    product_readiness: pd.DataFrame | list[dict[str, Any]],
    *,
    supplier_follow_up: pd.DataFrame | list[dict[str, Any]] | None = None,
    requirement_draft: pd.DataFrame | list[dict[str, Any]] | None = None,
    language: str = "en",
) -> pd.DataFrame:
    """Build one supplier comparison row per supplier.

    The function aggregates product readiness rows into supplier-level metrics
    so product teams can compare which supplier deserves the next sourcing or
    product-development action.
    """

    product_rows = _records(product_readiness)
    if not product_rows:
        return pd.DataFrame(columns=SUPPLIER_COMPARISON_COLUMNS)

    follow_up_counts = _source_url_counts(_records(supplier_follow_up))
    requirement_counts = _source_url_counts(_records(requirement_draft), field_name="current_value")

    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in product_rows:
        groups[supplier_group_key(row)].append(row)

    output_rows: list[dict[str, Any]] = []
    for supplier_key, rows in groups.items():
        scores = [_as_float(row.get("readiness_score")) for row in rows]
        completion_rates = [_as_float(row.get("completion_rate")) for row in rows]
        missing_counts = [_as_int(row.get("missing_count")) for row in rows]

        bucket_counts: Counter[str] = Counter(_status_bucket(row.get("readiness_status")) for row in rows)
        best_row = max(rows, key=lambda row: _as_float(row.get("readiness_score")))

        average_score = round(mean(scores), 2) if scores else 0.0
        max_score = round(max(scores), 2) if scores else 0.0
        average_completion = round(mean(completion_rates), 4) if completion_rates else 0.0
        total_follow_up = sum(
            follow_up_counts[str(row.get("source_url", "") or "").strip()]
            for row in rows
        )
        requirement_count = sum(
            requirement_counts[str(row.get("source_url", "") or "").strip()]
            for row in rows
        )

        status_key = _status_key(
            average_score,
            bucket_counts["high_risk"],
            bucket_counts["not_ready"],
        )
        lang = _language(language)

        output_rows.append(
            {
                "supplier_key": supplier_key,
                "supplier_name": _supplier_name(best_row),
                "domain": _domain_from_url(best_row.get("source_url")),
                "product_count": len(rows),
                "average_readiness_score": average_score,
                "max_readiness_score": max_score,
                "average_completion_rate": average_completion,
                "ready_product_count": bucket_counts["ready"],
                "follow_up_required_count": bucket_counts["follow_up"],
                "high_risk_product_count": bucket_counts["high_risk"],
                "not_ready_product_count": bucket_counts["not_ready"],
                "total_missing_fields": sum(missing_counts),
                "total_follow_up_questions": total_follow_up,
                "requirement_candidate_count": requirement_count,
                "best_product_title": str(best_row.get("title", "") or ""),
                "best_product_url": str(best_row.get("source_url", "") or ""),
                "overall_status": STATUS_LABELS[lang][status_key],
                "recommendation": RECOMMENDATIONS[lang][status_key],
                "next_action": NEXT_ACTIONS[lang][status_key],
            }
        )

    frame = pd.DataFrame(output_rows, columns=SUPPLIER_COMPARISON_COLUMNS)
    return frame.sort_values(
        by=["average_readiness_score", "max_readiness_score", "product_count"],
        ascending=[False, False, False],
        ignore_index=True,
    )

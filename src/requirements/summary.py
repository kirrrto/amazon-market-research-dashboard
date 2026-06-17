from __future__ import annotations

from typing import Any

import pandas as pd


RECOMMENDATIONS = {
    "en": {
        "low": "Ready for product review",
        "medium": "Supplier follow-up required before product definition",
        "high": "Not ready for product definition",
        "unknown": "Review required",
    },
    "zh-CN": {
        "low": "可以进入产品评审",
        "medium": "产品定义前需要供应商补充确认",
        "high": "暂不适合进入产品定义",
        "unknown": "需要人工复核",
    },
}

NEXT_ACTIONS = {
    "en": {
        "low": "Review commercial assumptions and continue engineering evaluation.",
        "medium": "Ask supplier to confirm missing specifications before finalizing requirements.",
        "high": "Collect missing technical data before committing product resources.",
        "unknown": "Review the source data and confirm whether gap analysis is complete.",
    },
    "zh-CN": {
        "low": "继续复核成本、售价和研发可行性。",
        "medium": "在确定产品需求前，先向供应商确认缺失规格。",
        "high": "先补齐关键技术数据，再投入产品定义资源。",
        "unknown": "请复核源数据，并确认缺口分析是否完整。",
    },
}


def _records(value: pd.DataFrame | list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    if value is None:
        return []
    if isinstance(value, pd.DataFrame):
        return value.to_dict("records")
    return list(value or [])


def _normalize_risk(value: Any) -> str:
    risk = str(value or "").strip().lower()
    return risk if risk in {"low", "medium", "high"} else "unknown"


def recommendation_for_risk(risk_level: str, language: str = "en") -> str:
    """Return a product decision recommendation for a risk level."""

    lang = "zh-CN" if language == "zh-CN" else "en"
    risk = _normalize_risk(risk_level)
    return RECOMMENDATIONS[lang][risk]


def _next_action_for_risk(risk_level: str, language: str = "en") -> str:
    lang = "zh-CN" if language == "zh-CN" else "en"
    risk = _normalize_risk(risk_level)
    return NEXT_ACTIONS[lang][risk]


def build_decision_summary(
    gap_analysis: pd.DataFrame | list[dict[str, Any]],
    *,
    language: str = "en",
) -> pd.DataFrame:
    """Build a product decision summary from gap analysis rows.

    The summary is intentionally conservative. It does not make a final product
    decision; it converts gap risk levels into review recommendations and next
    actions for product, sourcing and engineering teams.
    """

    columns = [
        "source_url",
        "title",
        "brand",
        "model",
        "profile",
        "profile_label",
        "risk_level",
        "missing_count",
        "required_fields_count",
        "completion_rate",
        "recommendation",
        "next_action",
        "missing_fields",
        "missing_labels",
        "decision_owner",
        "decision_status",
        "notes",
    ]

    rows: list[dict[str, Any]] = []
    for row in _records(gap_analysis):
        risk_level = _normalize_risk(row.get("risk_level"))
        missing_count = int(row.get("missing_count") or 0)
        required_count = int(row.get("required_fields_count") or 0)
        completion_rate = float(row.get("completion_rate") or 0)

        rows.append(
            {
                "source_url": str(row.get("source_url", "") or ""),
                "title": str(row.get("title", "") or ""),
                "brand": str(row.get("brand", "") or ""),
                "model": str(row.get("model", "") or ""),
                "profile": str(row.get("profile", "") or ""),
                "profile_label": str(row.get("profile_label", "") or ""),
                "risk_level": risk_level,
                "missing_count": missing_count,
                "required_fields_count": required_count,
                "completion_rate": round(completion_rate, 4),
                "recommendation": recommendation_for_risk(risk_level, language),
                "next_action": _next_action_for_risk(risk_level, language),
                "missing_fields": str(row.get("missing_fields", "") or ""),
                "missing_labels": str(row.get("missing_labels", "") or ""),
                "decision_owner": "",
                "decision_status": "Open" if language == "en" else "待处理",
                "notes": "",
            }
        )

    return pd.DataFrame(rows, columns=columns)

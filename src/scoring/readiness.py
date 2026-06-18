from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

import pandas as pd


READINESS_COLUMNS = [
    "source_url",
    "title",
    "brand",
    "model",
    "profile",
    "profile_label",
    "readiness_score",
    "readiness_status",
    "risk_level",
    "missing_count",
    "required_fields_count",
    "completion_rate",
    "metadata_completeness",
    "follow_up_question_count",
    "requirement_candidate_count",
    "recommendation",
    "next_action",
    "missing_fields",
    "missing_labels",
]

STATUS_LABELS = {
    "en": {
        "ready": "Ready for Review",
        "follow_up": "Follow-up Required",
        "high_risk": "High Risk",
        "not_ready": "Not Ready",
    },
    "zh-CN": {
        "ready": "可以进入评审",
        "follow_up": "需要补充确认",
        "high_risk": "高风险",
        "not_ready": "暂不建议继续",
    },
}

RECOMMENDATIONS = {
    "en": {
        "ready": "Continue product review and compare commercial assumptions.",
        "follow_up": "Continue supplier follow-up before requirement freeze.",
        "high_risk": "Treat as a high-risk candidate and resolve blocking gaps first.",
        "not_ready": "Do not invest product definition resources until core data is complete.",
    },
    "zh-CN": {
        "ready": "可以继续进入产品评审，并对比成本和商业假设。",
        "follow_up": "在冻结产品需求前，继续向供应商补充确认。",
        "high_risk": "作为高风险候选产品处理，先解决阻塞性缺口。",
        "not_ready": "核心资料补齐前，不建议投入产品定义资源。",
    },
}

NEXT_ACTIONS = {
    "en": {
        "ready": "Review pricing, cost, compliance and engineering feasibility.",
        "follow_up": "Send supplier follow-up questions and update the score after response.",
        "high_risk": "Block product definition until missing required specifications are resolved.",
        "not_ready": "Collect product metadata, required specifications and supplier documents first.",
    },
    "zh-CN": {
        "ready": "继续复核售价、成本、认证和研发可行性。",
        "follow_up": "发送供应商追问清单，收到回复后重新评分。",
        "high_risk": "缺失的必需规格解决前，暂缓产品定义。",
        "not_ready": "先补齐产品基础信息、必需规格和供应商资料。",
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


def _as_int(value: Any, default: int = 0) -> int:
    if _is_missing(value):
        return default
    try:
        return int(float(str(value).replace("%", "").strip()))
    except ValueError:
        return default


def _as_float(value: Any, default: float = 0.0) -> float:
    if _is_missing(value):
        return default
    try:
        number = float(str(value).replace("%", "").strip())
    except ValueError:
        return default
    return number / 100 if number > 1 else number


def _normalize_risk(value: Any) -> str:
    risk = str(value or "").strip().lower()
    return risk if risk in {"low", "medium", "high"} else "unknown"


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return min(max(float(value), low), high)


def _completion_rate(row: dict[str, Any]) -> float:
    explicit = row.get("completion_rate")
    if not _is_missing(explicit):
        return _clamp(_as_float(explicit), 0.0, 1.0)

    required_count = _as_int(row.get("required_fields_count"))
    missing_count = _as_int(row.get("missing_count"))
    if required_count <= 0:
        return 0.0

    return _clamp(1 - (missing_count / required_count), 0.0, 1.0)


def metadata_completeness(
    row: dict[str, Any],
    fields: Iterable[str] = ("source_url", "title", "brand", "model"),
) -> float:
    """Return metadata completeness from 0.0 to 1.0."""

    selected = list(fields)
    if not selected:
        return 1.0

    present = sum(0 if _is_missing(row.get(field)) else 1 for field in selected)
    return round(present / len(selected), 4)


def _follow_up_counts(
    supplier_follow_up: pd.DataFrame | list[dict[str, Any]] | None,
) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in _records(supplier_follow_up):
        source_url = str(row.get("source_url", "") or "").strip()
        if source_url:
            counts[source_url] += 1
    return counts


def _requirement_candidate_counts(
    requirement_draft: pd.DataFrame | list[dict[str, Any]] | None,
) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in _records(requirement_draft):
        source_url = str(row.get("source_url", "") or "").strip()
        current_value = row.get("current_value")
        if source_url and not _is_missing(current_value):
            counts[source_url] += 1
    return counts


def calculate_readiness_score(
    *,
    completion_rate: float,
    risk_level: str,
    metadata_score: float = 1.0,
    follow_up_question_count: int = 0,
    requirement_candidate_count: int = 0,
) -> float:
    """Calculate a 0-100 product readiness score.

    Score design:
    - 70 points: required specification completion
    - 20 points: gap risk control
    - 10 points: product metadata completeness
    - up to 5 bonus points: usable requirement candidates
    - up to 10 penalty points: unresolved supplier follow-up questions
    """

    risk = _normalize_risk(risk_level)
    risk_points = {
        "low": 20.0,
        "medium": 10.0,
        "high": 0.0,
        "unknown": 5.0,
    }[risk]

    base = _clamp(completion_rate, 0.0, 1.0) * 70.0
    metadata_points = _clamp(metadata_score, 0.0, 1.0) * 10.0
    requirement_bonus = min(max(requirement_candidate_count, 0) * 0.25, 5.0)
    follow_up_penalty = min(max(follow_up_question_count, 0) * 2.0, 10.0)

    return round(_clamp(base + risk_points + metadata_points + requirement_bonus - follow_up_penalty), 2)


def _status_key(score: float, risk_level: str) -> str:
    risk = _normalize_risk(risk_level)
    if score >= 80 and risk == "low":
        return "ready"
    if score >= 60 and risk != "high":
        return "follow_up"
    if score >= 40:
        return "high_risk"
    return "not_ready"


def readiness_status_for_score(score: float, risk_level: str, language: str = "en") -> str:
    """Map score and risk level to a human-readable readiness status."""

    lang = _language(language)
    return STATUS_LABELS[lang][_status_key(score, risk_level)]


def _recommendation_for_status(status_key: str, language: str = "en") -> str:
    return RECOMMENDATIONS[_language(language)][status_key]


def _next_action_for_status(status_key: str, language: str = "en") -> str:
    return NEXT_ACTIONS[_language(language)][status_key]


def build_product_readiness_summary(
    gap_analysis: pd.DataFrame | list[dict[str, Any]],
    *,
    supplier_follow_up: pd.DataFrame | list[dict[str, Any]] | None = None,
    requirement_draft: pd.DataFrame | list[dict[str, Any]] | None = None,
    language: str = "en",
) -> pd.DataFrame:
    """Build product readiness score rows from gap analysis outputs.

    This is a decision-support summary, not an automated final product decision.
    Product teams should use it to prioritize review, supplier follow-up and
    technical validation.
    """

    gap_rows = _records(gap_analysis)
    if not gap_rows:
        return pd.DataFrame(columns=READINESS_COLUMNS)

    follow_up_lookup = _follow_up_counts(supplier_follow_up)
    requirement_lookup = _requirement_candidate_counts(requirement_draft)

    rows: list[dict[str, Any]] = []
    for row in gap_rows:
        source_url = str(row.get("source_url", "") or "").strip()
        risk_level = _normalize_risk(row.get("risk_level"))
        completion = _completion_rate(row)
        metadata = metadata_completeness(row)
        follow_up_count = follow_up_lookup[source_url]
        requirement_count = requirement_lookup[source_url]

        score = calculate_readiness_score(
            completion_rate=completion,
            risk_level=risk_level,
            metadata_score=metadata,
            follow_up_question_count=follow_up_count,
            requirement_candidate_count=requirement_count,
        )
        status_key = _status_key(score, risk_level)

        rows.append(
            {
                "source_url": source_url,
                "title": str(row.get("title", "") or ""),
                "brand": str(row.get("brand", "") or ""),
                "model": str(row.get("model", "") or ""),
                "profile": str(row.get("profile", "") or ""),
                "profile_label": str(row.get("profile_label", "") or ""),
                "readiness_score": score,
                "readiness_status": STATUS_LABELS[_language(language)][status_key],
                "risk_level": risk_level,
                "missing_count": _as_int(row.get("missing_count")),
                "required_fields_count": _as_int(row.get("required_fields_count")),
                "completion_rate": round(completion, 4),
                "metadata_completeness": metadata,
                "follow_up_question_count": follow_up_count,
                "requirement_candidate_count": requirement_count,
                "recommendation": _recommendation_for_status(status_key, language),
                "next_action": _next_action_for_status(status_key, language),
                "missing_fields": str(row.get("missing_fields", "") or ""),
                "missing_labels": str(row.get("missing_labels", "") or ""),
            }
        )

    frame = pd.DataFrame(rows, columns=READINESS_COLUMNS)
    return frame.sort_values(
        by=["readiness_score", "completion_rate"],
        ascending=[False, False],
        ignore_index=True,
    )

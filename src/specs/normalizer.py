from __future__ import annotations

import re
from typing import Any

from .aliases import find_standard_field
from .fields import get_spec_field


def _clean_value(value: Any) -> str:
    text = str(value or "").strip()
    text = text.replace("：", ":")
    text = text.replace("～", " to ")
    text = text.replace("℃", "°C")
    text = text.replace("—", "-")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_spec_value(standard_field: str | None, raw_value: Any) -> str:
    value = _clean_value(raw_value)
    if not value:
        return ""

    if standard_field == "battery_capacity_mah":
        match = re.search(r"(\d+(?:\.\d+)?)\s*(mah|mAh|MAH)?", value, flags=re.IGNORECASE)
        if match:
            return f"{match.group(1)} mAh"

    if standard_field in {"operating_temperature", "storage_temperature"}:
        value = value.replace("°c", "°C")
        value = re.sub(r"\s*to\s*", " to ", value, flags=re.IGNORECASE)
        return value

    if standard_field == "waterproof_rating":
        match = re.search(r"\bIP\s*([0-9]{2}K?)\b", value, flags=re.IGNORECASE)
        if match:
            return f"IP{match.group(1).upper()}"

    if standard_field == "power_input":
        value = re.sub(r"\s*-\s*", "-", value)
        value = value.replace("DC:", "DC ")
        value = value.replace("DC：", "DC ")
        return value.strip()

    if standard_field in {"supports_rtsp", "supports_onvif"}:
        lowered = value.lower()
        if lowered in {"yes", "y", "true", "support", "supported", "支持", "是"}:
            return "Yes"
        if lowered in {"no", "n", "false", "not support", "unsupported", "不支持", "否"}:
            return "No"

    return value


def normalize_raw_specifications(raw_specs: list[dict[str, Any]], language: str = "en") -> list[dict[str, Any]]:
    """Map raw supplier specification rows to standard hardware fields.

    The function keeps raw evidence fields in every output row so users can
    review and override the automated mapping later.
    """

    rows: list[dict[str, Any]] = []
    for item in raw_specs:
        raw_name = str(item.get("spec_name") or item.get("name") or "").strip()
        raw_value = str(item.get("spec_value") or item.get("value") or "").strip()
        source_url = str(item.get("source_url", "")).strip()
        parser = str(item.get("parser", "")).strip()
        fetched_at = str(item.get("fetched_at", "")).strip()

        standard_field, confidence = find_standard_field(raw_name)
        if standard_field is None:
            continue

        field = get_spec_field(standard_field)
        rows.append(
            {
                "source_url": source_url,
                "standard_field": standard_field,
                "standard_label": field.label(language),
                "raw_spec_name": raw_name,
                "raw_spec_value": raw_value,
                "normalized_value": normalize_spec_value(standard_field, raw_value),
                "confidence": confidence,
                "category": field.category,
                "parser": parser,
                "fetched_at": fetched_at,
            }
        )

    return rows

from __future__ import annotations

from typing import Any

import pandas as pd

from src.specs.fields import get_spec_field


QUESTION_TEMPLATES: dict[str, dict[str, str]] = {
    "power_input": {
        "en": "Please confirm the power input range and connector power requirements for this product.",
        "zh-CN": "请确认该产品的供电输入范围，以及供电接口或线材要求。",
    },
    "operating_temperature": {
        "en": "Please confirm the operating temperature range and whether it has been validated under real use conditions.",
        "zh-CN": "请确认该产品的工作温度范围，以及是否经过真实使用环境验证。",
    },
    "storage_temperature": {
        "en": "Please confirm the storage temperature range for this product.",
        "zh-CN": "请确认该产品的存储温度范围。",
    },
    "waterproof_rating": {
        "en": "Please confirm the waterproof rating or IP protection level for this product.",
        "zh-CN": "请确认该产品的防水等级或 IP 防护等级。",
    },
    "dimensions": {
        "en": "Please provide the product dimensions, including main unit size and any external module dimensions.",
        "zh-CN": "请提供该产品的尺寸信息，包括主机尺寸和外置模块尺寸。",
    },
    "resolution": {
        "en": "Please confirm the video or image resolution and whether it is native or interpolated.",
        "zh-CN": "请确认视频或图像分辨率，并说明是原生分辨率还是插值分辨率。",
    },
    "camera_resolution": {
        "en": "Please confirm the camera resolution and video output format.",
        "zh-CN": "请确认摄像头分辨率和视频输出格式。",
    },
    "monitor_size": {
        "en": "Please confirm the monitor size and display panel type.",
        "zh-CN": "请确认显示器尺寸和屏幕面板类型。",
    },
    "monitor_resolution": {
        "en": "Please confirm the monitor display resolution.",
        "zh-CN": "请确认显示器分辨率。",
    },
    "wireless_protocol": {
        "en": "Please confirm the wireless protocol, frequency band and pairing method.",
        "zh-CN": "请确认无线协议、频段和配对方式。",
    },
    "transmission_range_m": {
        "en": "Please provide the tested wireless transmission range and test environment.",
        "zh-CN": "请提供无线传输距离的测试结果和测试环境。",
    },
    "latency_ms": {
        "en": "Please provide the measured video latency and test conditions.",
        "zh-CN": "请提供视频延迟测试数据和测试条件。",
    },
    "night_vision_type": {
        "en": "Please confirm the night vision type, infrared distance and whether full-color night vision is supported.",
        "zh-CN": "请确认夜视类型、红外距离，以及是否支持全彩夜视。",
    },
    "ir_distance_m": {
        "en": "Please confirm the infrared night vision distance in meters.",
        "zh-CN": "请确认红外夜视距离，单位为米。",
    },
    "battery_capacity_mah": {
        "en": "Please confirm the battery capacity, standby time and typical working time.",
        "zh-CN": "请确认电池容量、待机时间和典型工作时长。",
    },
    "supports_rtsp": {
        "en": "Please confirm whether RTSP is supported and provide the stream path format if available.",
        "zh-CN": "请确认是否支持 RTSP，如支持请提供视频流地址格式。",
    },
    "supports_onvif": {
        "en": "Please confirm whether ONVIF is supported and which profile is supported.",
        "zh-CN": "请确认是否支持 ONVIF，以及支持的 Profile 类型。",
    },
    "field_of_view": {
        "en": "Please confirm the lens field of view and whether the value is horizontal, vertical or diagonal.",
        "zh-CN": "请确认镜头视场角，并说明该数值是水平、垂直还是对角视场角。",
    },
    "anti_vibration": {
        "en": "Please confirm the anti-vibration or shock standard and related test evidence.",
        "zh-CN": "请确认抗震或冲击测试标准，并提供相关测试依据。",
    },
    "power_consumption": {
        "en": "Please confirm the typical and maximum power consumption.",
        "zh-CN": "请确认典型功耗和最大功耗。",
    },
}


def _records(value: pd.DataFrame | list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    if value is None:
        return []
    if isinstance(value, pd.DataFrame):
        return value.to_dict("records")
    return list(value or [])


def _field_label(standard_field: str, language: str = "en") -> str:
    try:
        return get_spec_field(standard_field).label(language)
    except KeyError:
        return standard_field


def question_for_field(standard_field: str, language: str = "en") -> str:
    """Return a supplier follow-up question for a missing specification field."""

    templates = QUESTION_TEMPLATES.get(standard_field)
    if templates:
        return templates.get(language) or templates["en"]

    if language == "zh-CN":
        return f"请确认该产品的“{_field_label(standard_field, language)}”参数。"
    return f"Please confirm the {standard_field} specification for this product."


def _split_missing_fields(value: Any) -> list[str]:
    if value is None:
        return []
    text = str(value).strip()
    if not text:
        return []
    return [item.strip() for item in text.split(",") if item.strip()]


def build_supplier_follow_up_questions(
    gap_analysis: pd.DataFrame | list[dict[str, Any]],
    *,
    language: str = "en",
) -> pd.DataFrame:
    """Convert missing-field gap analysis into supplier follow-up questions.

    One missing field becomes one question row, preserving product metadata and
    risk level so sourcing teams can prioritize supplier communication.
    """

    columns = [
        "source_url",
        "title",
        "brand",
        "model",
        "profile",
        "risk_level",
        "missing_field",
        "missing_label",
        "question",
        "priority",
        "owner",
        "status",
        "notes",
    ]

    rows: list[dict[str, Any]] = []
    for gap in _records(gap_analysis):
        missing_fields = _split_missing_fields(gap.get("missing_fields", ""))
        if not missing_fields:
            continue

        risk_level = str(gap.get("risk_level", "") or "").strip() or "unknown"
        priority = {
            "high": "High" if language == "en" else "高",
            "medium": "Medium" if language == "en" else "中",
            "low": "Low" if language == "en" else "低",
        }.get(risk_level, "Review" if language == "en" else "待确认")

        for field in missing_fields:
            rows.append(
                {
                    "source_url": str(gap.get("source_url", "") or ""),
                    "title": str(gap.get("title", "") or ""),
                    "brand": str(gap.get("brand", "") or ""),
                    "model": str(gap.get("model", "") or ""),
                    "profile": str(gap.get("profile", "") or ""),
                    "risk_level": risk_level,
                    "missing_field": field,
                    "missing_label": _field_label(field, language),
                    "question": question_for_field(field, language),
                    "priority": priority,
                    "owner": "",
                    "status": "Open" if language == "en" else "待处理",
                    "notes": "",
                }
            )

    return pd.DataFrame(rows, columns=columns)

from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher


SPEC_ALIASES: dict[str, tuple[str, ...]] = {
    "resolution": (
        "resolution",
        "video resolution",
        "image resolution",
        "recording resolution",
        "分辨率",
        "视频分辨率",
        "图像分辨率",
    ),
    "camera_resolution": (
        "camera resolution",
        "camera video resolution",
        "摄像头分辨率",
        "摄像头视频分辨率",
    ),
    "monitor_size": (
        "monitor size",
        "screen size",
        "display size",
        "lcd size",
        "显示器尺寸",
        "屏幕尺寸",
    ),
    "monitor_resolution": (
        "monitor resolution",
        "screen resolution",
        "display resolution",
        "显示器分辨率",
        "屏幕分辨率",
    ),
    "power_input": (
        "power supply",
        "power input",
        "dc input",
        "input voltage",
        "working voltage",
        "operating voltage",
        "voltage",
        "电源输入",
        "供电",
        "供电输入",
        "输入电压",
        "工作电压",
    ),
    "operating_temperature": (
        "operating temperature",
        "working temperature",
        "operating temp",
        "work temperature",
        "工作温度",
        "运行温度",
    ),
    "storage_temperature": (
        "storage temperature",
        "storage temp",
        "存储温度",
        "储存温度",
    ),
    "waterproof_rating": (
        "waterproof",
        "waterproof rating",
        "ip rating",
        "ip grade",
        "ingress protection",
        "waterproof level",
        "防水",
        "防水等级",
        "防护等级",
        "ip等级",
    ),
    "dimensions": (
        "dimension",
        "dimensions",
        "product size",
        "size",
        "box dimension",
        "dimension of multiplexer box",
        "尺寸",
        "产品尺寸",
        "外形尺寸",
    ),
    "battery_capacity_mah": (
        "battery capacity",
        "battery",
        "capacity",
        "电池容量",
        "电池",
    ),
    "wireless_protocol": (
        "wireless protocol",
        "wireless",
        "wifi",
        "wi-fi",
        "wifi band",
        "frequency",
        "transmission protocol",
        "无线协议",
        "无线",
        "wifi频段",
        "wi-fi频段",
        "传输协议",
    ),
    "transmission_range_m": (
        "transmission range",
        "wireless range",
        "range",
        "transmission distance",
        "传输距离",
        "无线距离",
    ),
    "latency_ms": (
        "latency",
        "delay",
        "video delay",
        "延迟",
        "视频延迟",
    ),
    "night_vision_type": (
        "night vision",
        "night vision type",
        "ir night vision",
        "full color night vision",
        "夜视",
        "夜视类型",
        "红外夜视",
        "全彩夜视",
    ),
    "ir_distance_m": (
        "ir distance",
        "infrared distance",
        "night vision distance",
        "红外距离",
        "红外夜视距离",
        "夜视距离",
    ),
    "supports_rtsp": (
        "rtsp",
        "supports rtsp",
        "rtsp support",
        "支持rtsp",
        "rtsp支持",
    ),
    "supports_onvif": (
        "onvif",
        "supports onvif",
        "onvif support",
        "支持onvif",
        "onvif支持",
    ),
    "field_of_view": (
        "field of view",
        "fov",
        "view angle",
        "lens angle",
        "angle",
        "视场角",
        "镜头角度",
        "可视角度",
    ),
    "anti_vibration": (
        "anti-vibration",
        "anti vibration",
        "vibration",
        "shock",
        "抗震",
        "防震",
        "震动",
    ),
    "power_consumption": (
        "power consumption",
        "consumption",
        "功耗",
        "耗电",
    ),
}


def normalize_alias_key(value: str) -> str:
    text = unicodedata.normalize("NFKC", str(value or "")).strip().lower()
    text = text.replace("℃", "°c")
    return re.sub(r"[\W_]+", "", text, flags=re.UNICODE)


ALIAS_TO_FIELD: dict[str, str] = {}
for standard_field, aliases in SPEC_ALIASES.items():
    ALIAS_TO_FIELD[normalize_alias_key(standard_field)] = standard_field
    for alias in aliases:
        ALIAS_TO_FIELD[normalize_alias_key(alias)] = standard_field


def find_standard_field(raw_name: str) -> tuple[str | None, float]:
    """Return the best standard field match and a confidence score.

    Exact alias matches receive high confidence. Partial and fuzzy matches are
    intentionally lower confidence because raw supplier specification names are
    inconsistent and should remain auditable.
    """

    normalized = normalize_alias_key(raw_name)
    if not normalized:
        return None, 0.0

    exact = ALIAS_TO_FIELD.get(normalized)
    if exact is not None:
        return exact, 1.0

    # Containment match for names like "Dimension of Multiplexer Box".
    containment_candidates: list[tuple[int, str]] = []
    for alias, field in ALIAS_TO_FIELD.items():
        if len(alias) < 4:
            continue
        if alias in normalized or normalized in alias:
            containment_candidates.append((len(alias), field))

    if containment_candidates:
        containment_candidates.sort(reverse=True)
        return containment_candidates[0][1], 0.82

    # Fuzzy match as low-confidence fallback.
    best_field: str | None = None
    best_score = 0.0
    for alias, field in ALIAS_TO_FIELD.items():
        score = SequenceMatcher(None, normalized, alias).ratio()
        if score > best_score:
            best_score = score
            best_field = field

    if best_field and best_score >= 0.84:
        return best_field, round(best_score * 0.75, 2)

    return None, 0.0

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SpecificationField:
    standard_field: str
    label_en: str
    label_zh: str
    category: str
    description_en: str
    description_zh: str
    unit_hint: str = ""

    def label(self, language: str = "en") -> str:
        return self.label_zh if language == "zh-CN" else self.label_en


SPECIFICATION_FIELDS: tuple[SpecificationField, ...] = (
    SpecificationField(
        "resolution",
        "Resolution",
        "分辨率",
        "image",
        "Generic image or video resolution.",
        "通用图像或视频分辨率。",
    ),
    SpecificationField(
        "camera_resolution",
        "Camera Resolution",
        "摄像头分辨率",
        "vehicle_imaging",
        "Camera video resolution.",
        "摄像头视频分辨率。",
    ),
    SpecificationField(
        "monitor_size",
        "Monitor Size",
        "显示器尺寸",
        "vehicle_imaging",
        "Vehicle monitor display size.",
        "车载显示器尺寸。",
        "inch",
    ),
    SpecificationField(
        "monitor_resolution",
        "Monitor Resolution",
        "显示器分辨率",
        "vehicle_imaging",
        "Vehicle monitor display resolution.",
        "车载显示器分辨率。",
    ),
    SpecificationField(
        "power_input",
        "Power Input",
        "供电输入",
        "electrical",
        "Power supply or DC input range.",
        "供电或直流输入范围。",
        "V",
    ),
    SpecificationField(
        "operating_temperature",
        "Operating Temperature",
        "工作温度",
        "environment",
        "Operating temperature range.",
        "工作温度范围。",
        "°C",
    ),
    SpecificationField(
        "storage_temperature",
        "Storage Temperature",
        "存储温度",
        "environment",
        "Storage temperature range.",
        "存储温度范围。",
        "°C",
    ),
    SpecificationField(
        "waterproof_rating",
        "Waterproof Rating",
        "防水等级",
        "environment",
        "IP waterproof or ingress protection rating.",
        "IP防水或防护等级。",
    ),
    SpecificationField(
        "dimensions",
        "Dimensions",
        "尺寸",
        "mechanical",
        "Product or component dimensions.",
        "产品或部件尺寸。",
        "mm",
    ),
    SpecificationField(
        "battery_capacity_mah",
        "Battery Capacity",
        "电池容量",
        "battery",
        "Battery capacity in mAh.",
        "电池容量，单位mAh。",
        "mAh",
    ),
    SpecificationField(
        "wireless_protocol",
        "Wireless Protocol",
        "无线协议",
        "wireless",
        "Wireless transmission protocol or frequency band.",
        "无线传输协议或频段。",
    ),
    SpecificationField(
        "transmission_range_m",
        "Transmission Range",
        "传输距离",
        "wireless",
        "Wireless or video transmission range.",
        "无线或视频传输距离。",
        "m",
    ),
    SpecificationField(
        "latency_ms",
        "Latency",
        "延迟",
        "vehicle_imaging",
        "Video latency.",
        "视频延迟。",
        "ms",
    ),
    SpecificationField(
        "night_vision_type",
        "Night Vision Type",
        "夜视类型",
        "security_camera",
        "IR, full-color or dual-light night vision type.",
        "红外、全彩或双光夜视类型。",
    ),
    SpecificationField(
        "ir_distance_m",
        "IR Distance",
        "红外距离",
        "security_camera",
        "Infrared night vision range.",
        "红外夜视距离。",
        "m",
    ),
    SpecificationField(
        "supports_rtsp",
        "Supports RTSP",
        "支持RTSP",
        "network",
        "Whether RTSP streaming is supported.",
        "是否支持RTSP视频流。",
    ),
    SpecificationField(
        "supports_onvif",
        "Supports ONVIF",
        "支持ONVIF",
        "network",
        "Whether ONVIF is supported.",
        "是否支持ONVIF。",
    ),
    SpecificationField(
        "field_of_view",
        "Field of View",
        "视场角",
        "optics",
        "Lens angle or field of view.",
        "镜头角度或视场角。",
        "degree",
    ),
    SpecificationField(
        "anti_vibration",
        "Anti-vibration",
        "抗震",
        "reliability",
        "Anti-vibration or shock standard.",
        "抗震或冲击标准。",
    ),
    SpecificationField(
        "power_consumption",
        "Power Consumption",
        "功耗",
        "electrical",
        "Power consumption.",
        "功耗。",
        "W",
    ),
)


SPEC_FIELD_BY_NAME = {field.standard_field: field for field in SPECIFICATION_FIELDS}


def list_spec_fields() -> tuple[SpecificationField, ...]:
    return SPECIFICATION_FIELDS


def get_spec_field(standard_field: str) -> SpecificationField:
    try:
        return SPEC_FIELD_BY_NAME[standard_field]
    except KeyError as exc:
        raise KeyError(f"Unknown standard specification field: {standard_field}") from exc

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SpecProfile:
    profile_id: str
    label_en: str
    label_zh: str
    description_en: str
    description_zh: str
    required_fields: tuple[str, ...]

    def label(self, language: str = "en") -> str:
        return self.label_zh if language == "zh-CN" else self.label_en

    def description(self, language: str = "en") -> str:
        return self.description_zh if language == "zh-CN" else self.description_en


SPEC_PROFILES: tuple[SpecProfile, ...] = (
    SpecProfile(
        profile_id="generic_hardware",
        label_en="Generic Hardware",
        label_zh="通用硬件",
        description_en="Baseline profile for general hardware product research.",
        description_zh="适用于通用硬件产品调研的基础字段组合。",
        required_fields=(
            "power_input",
            "operating_temperature",
            "dimensions",
        ),
    ),
    SpecProfile(
        profile_id="security_camera",
        label_en="Security Camera",
        label_zh="安防摄像头",
        description_en="Required field profile for security camera product definition.",
        description_zh="适用于安防摄像头产品定义的必需字段组合。",
        required_fields=(
            "resolution",
            "night_vision_type",
            "waterproof_rating",
            "operating_temperature",
            "wireless_protocol",
            "battery_capacity_mah",
            "supports_rtsp",
            "supports_onvif",
        ),
    ),
    SpecProfile(
        profile_id="vehicle_camera",
        label_en="Vehicle Imaging",
        label_zh="车载影像",
        description_en="Required field profile for backup cameras, monitors and vehicle imaging systems.",
        description_zh="适用于倒车摄像头、车载显示器和车载影像系统的必需字段组合。",
        required_fields=(
            "camera_resolution",
            "monitor_size",
            "power_input",
            "waterproof_rating",
            "operating_temperature",
            "wireless_protocol",
            "latency_ms",
            "transmission_range_m",
        ),
    ),
)


SPEC_PROFILE_BY_ID = {profile.profile_id: profile for profile in SPEC_PROFILES}


def list_spec_profiles() -> tuple[SpecProfile, ...]:
    return SPEC_PROFILES


def get_spec_profile(profile_id: str) -> SpecProfile:
    try:
        return SPEC_PROFILE_BY_ID[profile_id]
    except KeyError as exc:
        raise KeyError(f"Unknown specification profile: {profile_id}") from exc

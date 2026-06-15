from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TemplateField:
    name: str
    label_en: str
    label_zh: str
    description_en: str
    description_zh: str
    example: str
    required: bool = False


@dataclass(frozen=True)
class TemplateDefinition:
    template_id: str
    file_name: str
    sheet_key: str
    title_en: str
    title_zh: str
    description_en: str
    description_zh: str
    fields: tuple[TemplateField, ...]

    def title(self, language: str = "en") -> str:
        return self.title_zh if language == "zh-CN" else self.title_en

    def description(self, language: str = "en") -> str:
        return self.description_zh if language == "zh-CN" else self.description_en


def _field(
    name: str,
    label_en: str,
    label_zh: str,
    description_en: str,
    description_zh: str,
    example: str = "",
    required: bool = False,
) -> TemplateField:
    return TemplateField(
        name=name,
        label_en=label_en,
        label_zh=label_zh,
        description_en=description_en,
        description_zh=description_zh,
        example=example,
        required=required,
    )


MARKET_RESEARCH_FIELDS = (
    _field("asin", "ASIN", "ASIN", "Amazon product identifier.", "亚马逊商品标识。", "B0XXXXXXX", True),
    _field("title", "Title", "标题", "Product title.", "产品标题。", "Wireless Backup Camera", True),
    _field("brand", "Brand", "品牌", "Brand name.", "品牌名称。", "STONKAM", True),
    _field("price", "Price", "价格", "Current selling price.", "当前售价。", "89.99", True),
    _field("rating", "Rating", "评分", "Average customer rating.", "平均评分。", "4.3", True),
    _field("reviews", "Reviews", "评论数", "Review count.", "评论数量。", "860", True),
    _field("monthly_sales", "Monthly Sales", "月销量", "Estimated monthly unit sales.", "预估月销量。", "420", True),
    _field("category", "Category", "类目", "Product category.", "产品类目。", "Vehicle Camera", True),
    _field("source", "Source", "来源", "Data source or tool name.", "数据来源或工具名称。", "Helium 10 export"),
    _field("notes", "Notes", "备注", "Research notes.", "调研备注。", "Check supplier cost"),
)

SUPPLIER_QUOTE_FIELDS = (
    _field("supplier_name", "Supplier Name", "供应商名称", "Supplier or factory name.", "供应商或工厂名称。", "Supplier A", True),
    _field("contact", "Contact", "联系人", "Contact person or channel.", "联系人或联系方式。", "sales@example.com"),
    _field("product_model", "Product Model", "产品型号", "Supplier model number.", "供应商产品型号。", "CAM-001", True),
    _field("moq", "MOQ", "最小起订量", "Minimum order quantity.", "最小起订量。", "500"),
    _field("unit_cost", "Unit Cost", "单价", "Quoted unit cost.", "报价单价。", "32.50", True),
    _field("sample_cost", "Sample Cost", "样品费", "Sample cost.", "样品费用。", "80"),
    _field("lead_time_days", "Lead Time Days", "交期天数", "Estimated lead time in days.", "预计交期天数。", "35"),
    _field("certifications", "Certifications", "认证", "Available certifications.", "已有认证。", "FCC, CE, RoHS"),
    _field("app_solution", "App Solution", "APP方案", "App or platform solution.", "APP或平台方案。", "Tuya / private app"),
    _field("firmware_ownership", "Firmware Ownership", "固件归属", "Firmware ownership and update responsibility.", "固件归属和升级责任。", "Supplier controls firmware"),
    _field("private_server_support", "Private Server Support", "私有服务器支持", "Whether private server deployment is supported.", "是否支持私有服务器部署。", "Yes"),
    _field("notes", "Notes", "备注", "Supplier evaluation notes.", "供应商评估备注。", "Need NDA before SDK review"),
)

PRODUCT_URL_FIELDS = (
    _field("source_url", "Source URL", "来源链接", "Public product page URL.", "公开产品页面链接。", "https://example.com/product-a", True),
    _field("brand", "Brand", "品牌", "Brand or supplier name.", "品牌或供应商名称。", "STONKAM"),
    _field("category", "Category", "类目", "Product category.", "产品类目。", "Vehicle Camera"),
    _field("priority", "Priority", "优先级", "Collection priority.", "采集优先级。", "High"),
    _field("notes", "Notes", "备注", "Collection notes.", "采集备注。", "Supplier main product page"),
)

SECURITY_CAMERA_FIELDS = (
    _field("brand", "Brand", "品牌", "Brand name.", "品牌名称。", "Reolink", True),
    _field("model", "Model", "型号", "Product model.", "产品型号。", "CAM-4G-001", True),
    _field("resolution", "Resolution", "分辨率", "Video or image resolution.", "视频或图像分辨率。", "2K"),
    _field("sensor", "Sensor", "传感器", "Image sensor.", "图像传感器。", "1/2.8 inch CMOS"),
    _field("lens_angle", "Lens Angle", "镜头角度", "Field of view.", "视场角。", "120°"),
    _field("night_vision_type", "Night Vision Type", "夜视类型", "IR, full-color or dual-light night vision.", "红外、全彩或双光夜视。", "IR + spotlight"),
    _field("ir_distance_m", "IR Distance (m)", "红外距离（米）", "IR night vision range in meters.", "红外夜视距离，单位米。", "15"),
    _field("wifi_band", "Wi-Fi Band", "Wi-Fi频段", "Supported Wi-Fi bands.", "支持的 Wi-Fi 频段。", "2.4GHz"),
    _field("supports_4g", "Supports 4G", "支持4G", "Whether cellular 4G is supported.", "是否支持4G蜂窝网络。", "Yes"),
    _field("supports_rtsp", "Supports RTSP", "支持RTSP", "Whether RTSP is supported.", "是否支持RTSP。", "No"),
    _field("supports_onvif", "Supports ONVIF", "支持ONVIF", "Whether ONVIF is supported.", "是否支持ONVIF。", "No"),
    _field("battery_capacity_mah", "Battery Capacity (mAh)", "电池容量（mAh）", "Battery capacity in mAh.", "电池容量，单位mAh。", "5200"),
    _field("solar_panel", "Solar Panel", "太阳能板", "Solar panel support.", "太阳能板支持情况。", "Optional"),
    _field("storage_type", "Storage Type", "存储方式", "Local, cloud or hybrid storage.", "本地、云或混合存储。", "SD card + cloud"),
    _field("waterproof_rating", "Waterproof Rating", "防水等级", "IP waterproof rating.", "IP防护等级。", "IP66"),
    _field("operating_temperature", "Operating Temperature", "工作温度", "Operating temperature range.", "工作温度范围。", "-20°C to 60°C"),
    _field("app_name", "App Name", "APP名称", "Mobile app name.", "移动端APP名称。", "ExampleCam"),
    _field("cloud_service", "Cloud Service", "云服务", "Cloud service or subscription model.", "云服务或订阅模式。", "Optional subscription"),
    _field("notes", "Notes", "备注", "Specification notes.", "规格备注。", "Check battery life in winter"),
)

VEHICLE_CAMERA_FIELDS = (
    _field("brand", "Brand", "品牌", "Brand name.", "品牌名称。", "STONKAM", True),
    _field("model", "Model", "型号", "Product model.", "产品型号。", "FHD642M", True),
    _field("camera_resolution", "Camera Resolution", "摄像头分辨率", "Camera video resolution.", "摄像头视频分辨率。", "1080P"),
    _field("monitor_size", "Monitor Size", "显示器尺寸", "Monitor size.", "显示器尺寸。", "7 inch"),
    _field("monitor_resolution", "Monitor Resolution", "显示器分辨率", "Monitor resolution.", "显示器分辨率。", "1024 × 600"),
    _field("wireless_protocol", "Wireless Protocol", "无线协议", "Wireless or transmission protocol.", "无线或传输协议。", "2.4GHz digital wireless"),
    _field("latency_ms", "Latency (ms)", "延迟（毫秒）", "Video latency in milliseconds.", "视频延迟，单位毫秒。", "120"),
    _field("transmission_range_m", "Transmission Range (m)", "传输距离（米）", "Transmission range in meters.", "传输距离，单位米。", "100"),
    _field("camera_quantity", "Camera Quantity", "摄像头数量", "Supported number of cameras.", "支持摄像头数量。", "2"),
    _field("parking_guidelines", "Parking Guidelines", "倒车辅助线", "Parking guideline support.", "倒车辅助线支持情况。", "Yes"),
    _field("power_input", "Power Input", "供电输入", "Power input range.", "供电输入范围。", "DC 10-32V"),
    _field("connector_type", "Connector Type", "接口类型", "Connector or cable type.", "接口或线材类型。", "4-pin aviation"),
    _field("mounting_method", "Mounting Method", "安装方式", "Installation method.", "安装方式。", "Bracket"),
    _field("waterproof_rating", "Waterproof Rating", "防水等级", "IP waterproof rating.", "IP防护等级。", "IP69K"),
    _field("operating_temperature", "Operating Temperature", "工作温度", "Operating temperature range.", "工作温度范围。", "-20°C to 70°C"),
    _field("recording_support", "Recording Support", "录像支持", "Recording support.", "录像支持情况。", "Optional DVR"),
    _field("carplay_interference_risk", "CarPlay Interference Risk", "CarPlay干扰风险", "Potential interference with CarPlay or Android Auto.", "与CarPlay或Android Auto的潜在干扰风险。", "Needs testing"),
    _field("notes", "Notes", "备注", "Specification notes.", "规格备注。", "Verify wireless range behind trailer"),
)

TEMPLATE_DEFINITIONS: tuple[TemplateDefinition, ...] = (
    TemplateDefinition(
        template_id="market_research",
        file_name="market_research_template.xlsx",
        sheet_key="products",
        title_en="Market Research Template",
        title_zh="市场调研模板",
        description_en="Template for Amazon product research and market analysis inputs.",
        description_zh="用于亚马逊产品调研和市场分析输入的模板。",
        fields=MARKET_RESEARCH_FIELDS,
    ),
    TemplateDefinition(
        template_id="supplier_quote",
        file_name="supplier_quote_template.xlsx",
        sheet_key="supplier_quotes",
        title_en="Supplier Quote Template",
        title_zh="供应商报价模板",
        description_en="Template for supplier quotes, MOQ, lead time and technical capability records.",
        description_zh="用于记录供应商报价、MOQ、交期和技术能力的模板。",
        fields=SUPPLIER_QUOTE_FIELDS,
    ),
    TemplateDefinition(
        template_id="product_url_import",
        file_name="product_url_import_template.xlsx",
        sheet_key="product_urls",
        title_en="Product URL Import Template",
        title_zh="产品URL导入模板",
        description_en="Template for collecting public supplier and brand product page URLs.",
        description_zh="用于整理公开供应商和品牌产品页面URL的模板。",
        fields=PRODUCT_URL_FIELDS,
    ),
    TemplateDefinition(
        template_id="security_camera_specs",
        file_name="security_camera_spec_template.xlsx",
        sheet_key="security_camera_specs",
        title_en="Security Camera Specification Template",
        title_zh="安防摄像头规格模板",
        description_en="Template for security camera hardware and software specifications.",
        description_zh="用于安防摄像头硬件与软件规格收集的模板。",
        fields=SECURITY_CAMERA_FIELDS,
    ),
    TemplateDefinition(
        template_id="vehicle_camera_specs",
        file_name="vehicle_camera_spec_template.xlsx",
        sheet_key="vehicle_camera_specs",
        title_en="Vehicle Camera Specification Template",
        title_zh="车载影像规格模板",
        description_en="Template for backup cameras, vehicle monitors and wireless imaging systems.",
        description_zh="用于倒车摄像头、车载显示器和无线影像系统规格收集的模板。",
        fields=VEHICLE_CAMERA_FIELDS,
    ),
)


def list_template_definitions() -> tuple[TemplateDefinition, ...]:
    return TEMPLATE_DEFINITIONS


def get_template_definition(template_id: str) -> TemplateDefinition:
    for definition in TEMPLATE_DEFINITIONS:
        if definition.template_id == template_id:
            return definition
    raise KeyError(f"Unknown template_id: {template_id}")

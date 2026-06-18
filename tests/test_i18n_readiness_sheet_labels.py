from src.i18n import sheet_label, t


def test_readiness_export_sheet_labels_are_formal_names():
    assert sheet_label("product_readiness_summary", "en") == "Product Readiness Summary"
    assert sheet_label("supplier_comparison", "en") == "Supplier Comparison"
    assert sheet_label("product_pool_summary", "en") == "Product Pool Summary"


def test_readiness_export_sheet_labels_are_formal_chinese_names():
    assert sheet_label("product_readiness_summary", "zh-CN") == "产品就绪度汇总"
    assert sheet_label("supplier_comparison", "zh-CN") == "供应商对比"
    assert sheet_label("product_pool_summary", "zh-CN") == "产品池汇总"


def test_readiness_ui_labels_remain_short():
    assert t("product_readiness_summary", "en") == "Readiness Score"
    assert t("supplier_comparison", "en") == "Supplier Comparison"
    assert t("product_pool_summary", "en") == "Product Pool"

    assert t("product_readiness_summary", "zh-CN") == "就绪度评分"
    assert t("supplier_comparison", "zh-CN") == "供应商对比"
    assert t("product_pool_summary", "zh-CN") == "产品池"

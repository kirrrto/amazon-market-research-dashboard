from src.i18n import sheet_label, t


def test_requirement_export_sheet_labels_are_full_names():
    assert sheet_label("requirement_draft", "en") == "Product Requirement Draft"
    assert sheet_label("supplier_follow_up", "en") == "Supplier Follow-up Questions"
    assert sheet_label("decision_summary", "en") == "Decision Summary"


def test_requirement_export_sheet_labels_are_full_chinese_names():
    assert sheet_label("requirement_draft", "zh-CN") == "产品需求草案"
    assert sheet_label("supplier_follow_up", "zh-CN") == "供应商追问清单"
    assert sheet_label("decision_summary", "zh-CN") == "决策摘要"


def test_requirement_ui_labels_remain_short():
    assert t("requirement_draft", "en") == "Requirement Draft"
    assert t("supplier_follow_up", "en") == "Supplier Follow-up"
    assert t("requirement_draft", "zh-CN") == "需求草案"
    assert t("supplier_follow_up", "zh-CN") == "供应商追问"

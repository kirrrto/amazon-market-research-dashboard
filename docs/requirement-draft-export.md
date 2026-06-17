# Product Requirement Draft and Supplier Follow-up Export

## Purpose

The Product Requirement Draft workflow converts specification matrix and gap analysis results into practical product development outputs.

Before this module, users could already see:

- extracted raw specifications,
- normalized specifications,
- specification matrix,
- coverage summary,
- missing fields,
- risk level.

However, product developers still had to manually turn those findings into:

- a product requirement draft,
- supplier follow-up questions,
- internal decision notes.

This module automates that first draft.

## Outputs

The product page connector export now includes three additional sheets.

### Product Requirement Draft

This sheet converts specification matrix values into requirement draft rows.

Core columns:

```text
source_url
title
brand
model
profile
risk_level
requirement_field
requirement_label
current_value
evidence_source
action
notes
```

Example:

| requirement_field | current_value | evidence_source | action |
|---|---|---|---|
| power_input | DC 10-32V | Specification Matrix | Keep as candidate requirement |
| waterproof_rating |  | Gap Analysis | Supplier follow-up required |

Use this sheet as an early product requirement input, not as a final engineering specification.

### Supplier Follow-up Questions

This sheet turns missing fields into supplier questions.

Core columns:

```text
source_url
title
brand
model
profile
risk_level
missing_field
missing_label
question
priority
owner
status
notes
```

Example:

```text
missing_field: waterproof_rating
question: Please confirm the waterproof rating or IP protection level for this product.
```

Chinese example:

```text
missing_field: waterproof_rating
question: 请确认该产品的防水等级或 IP 防护等级。
```

### Decision Summary

This sheet summarizes product readiness based on gap risk level.

Core columns:

```text
source_url
title
brand
model
profile
profile_label
risk_level
missing_count
required_fields_count
completion_rate
recommendation
next_action
missing_fields
missing_labels
decision_owner
decision_status
notes
```

Risk-level recommendations:

| Risk level | Recommendation |
|---|---|
| low | Ready for product review |
| medium | Supplier follow-up required before product definition |
| high | Not ready for product definition |
| unknown | Review required |

Chinese recommendations:

| 风险等级 | 建议 |
|---|---|
| low | 可以进入产品评审 |
| medium | 产品定义前需要供应商补充确认 |
| high | 暂不适合进入产品定义 |
| unknown | 需要人工复核 |

## Recommended workflow

```text
Fetch product pages
→ Review Normalized Specifications
→ Review Specification Matrix
→ Review Gap Analysis
→ Open Product Requirement Draft
→ Send Supplier Follow-up Questions
→ Review Decision Summary
→ Decide whether to continue product definition
```

## How product teams should use it

### Product developers

Use the requirement draft as a structured starting point for defining product parameters.

Example:

```text
Power input: DC 10-32V
Operating temperature: -20°C to 70°C
Waterproof rating: missing
Action: ask supplier before requirement freeze
```

### Sourcing teams

Use supplier follow-up questions to request missing technical data from suppliers.

Example:

```text
Please confirm:
- waterproof rating
- latency
- wireless transmission range
- operating temperature
```

### Engineering teams

Use the decision summary to understand whether the product data is ready for technical evaluation.

Example:

```text
Risk level: high
Recommendation: Not ready for product definition
Next action: Collect missing technical data before committing product resources.
```

## Important limitations

The output is a draft.

It does not:

- replace engineering validation,
- replace supplier audit,
- replace certification review,
- make final product decisions,
- verify whether supplier claims are true,
- send supplier emails automatically.

Users should review all generated rows before using them in formal product requirement documents.

## Future improvements

Planned improvements include:

- product requirement table export for engineering teams,
- supplier scoring integration,
- compliance matrix integration,
- Word / PDF requirement report export,
- supplier-specific follow-up templates,
- project stage and owner tracking.

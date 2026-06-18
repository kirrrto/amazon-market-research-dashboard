# Product Readiness Score and Supplier Comparison

## Purpose

The Product Readiness Score and Supplier Comparison workflow turns specification analysis into a higher-level product development decision view.

Before this module, users could review:

- raw specifications,
- normalized specifications,
- specification matrix,
- coverage summary,
- gap analysis,
- product requirement draft,
- supplier follow-up questions,
- decision summary.

This module adds product-level and supplier-level prioritization.

It helps product developers answer:

- Which product is closest to product review readiness?
- Which product still needs supplier follow-up?
- Which supplier has stronger product data quality?
- Which product should be treated as high risk?
- Which product should remain in the product pool but not enter review yet?

## New outputs

The product page connector workbook now includes three additional sheets.

### Product Readiness Summary

This sheet scores each product from 0 to 100.

Core columns:

```text
source_url
title
brand
model
profile
profile_label
readiness_score
readiness_status
risk_level
missing_count
required_fields_count
completion_rate
metadata_completeness
follow_up_question_count
requirement_candidate_count
recommendation
next_action
missing_fields
missing_labels
```

### Supplier Comparison

This sheet aggregates products by supplier.

Core columns:

```text
supplier_key
supplier_name
domain
product_count
average_readiness_score
max_readiness_score
average_completion_rate
ready_product_count
follow_up_required_count
high_risk_product_count
not_ready_product_count
total_missing_fields
total_follow_up_questions
requirement_candidate_count
best_product_title
best_product_url
overall_status
recommendation
next_action
```

### Product Pool Summary

This sheet creates a product pool view for prioritization.

Core columns:

```text
source_url
title
brand
model
supplier_key
supplier_name
domain
readiness_score
readiness_status
product_pool_status
priority
risk_level
completion_rate
metadata_completeness
missing_count
required_fields_count
follow_up_question_count
requirement_candidate_count
supplier_average_readiness_score
supplier_overall_status
recommendation
next_action
missing_fields
missing_labels
```

## Scoring logic

The readiness score is calculated from five components.

```text
70 points: required specification completion
20 points: gap risk control
10 points: product metadata completeness
up to +5 points: usable requirement candidates
up to -10 points: unresolved supplier follow-up questions
```

The score is intentionally conservative. It is not a final launch decision. It is a product development prioritization signal.

## Readiness status

| Score / risk condition | Status |
|---|---|
| Score >= 80 and low risk | Ready for Review |
| Score >= 60 and not high risk | Follow-up Required |
| Score >= 40 | High Risk |
| Score < 40 | Not Ready |

Chinese status labels:

| English | Chinese |
|---|---|
| Ready for Review | 可以进入评审 |
| Follow-up Required | 需要补充确认 |
| High Risk | 高风险 |
| Not Ready | 暂不建议继续 |

## Product pool priority

| Priority | Status | Meaning |
|---|---|---|
| P1 | Review Candidate | Candidate for product review |
| P2 | Supplier Follow-up | Keep in pool and ask supplier questions |
| P3 | Risk Review | Risk review before resource allocation |
| P4 | Hold | Low priority reference only |

## Recommended product workflow

```text
Import product URLs
→ Review extracted specifications
→ Review Specification Matrix
→ Review Gap Analysis
→ Review Product Requirement Draft
→ Send Supplier Follow-up Questions
→ Review Product Readiness Summary
→ Compare Supplier Comparison
→ Filter Product Pool Summary
→ Select products for review or supplier follow-up
```

## How product teams should interpret the score

### 80-100

The product may be ready for product review, especially when risk level is low.

Recommended action:

```text
Compare quote, MOQ, lead time, certification documents and engineering feasibility.
```

### 60-79

The product is a possible candidate, but supplier follow-up is still required.

Recommended action:

```text
Send supplier follow-up questions and update readiness score after receiving a response.
```

### 40-59

The product has meaningful data or technical gaps.

Recommended action:

```text
Resolve missing required fields before assigning engineering or sourcing resources.
```

### Below 40

The product is not ready for product definition.

Recommended action:

```text
Collect product metadata, required specifications and supplier documents first.
```

## How sourcing teams should use Supplier Comparison

Supplier Comparison is useful when multiple products or multiple suppliers are being evaluated for the same product direction.

Use it to compare:

- average readiness score,
- maximum readiness score,
- total missing fields,
- total follow-up questions,
- number of ready candidates,
- number of high-risk products,
- best candidate product.

A supplier with a high maximum score but low average score may have one strong candidate but an inconsistent product line.

A supplier with high average readiness and low missing-field count should receive higher sourcing priority.

## Limitations

This module does not:

- verify supplier claims,
- replace supplier audit,
- replace engineering validation,
- replace certification review,
- calculate true market demand,
- make final product launch decisions.

It is a decision-support layer for product development and sourcing prioritization.

## Future improvements

Planned improvements include:

- supplier quote comparison,
- compliance document scoring,
- market opportunity scoring,
- review and VOC scoring,
- product report builder,
- engineering requirement export.

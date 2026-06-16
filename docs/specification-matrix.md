# Specification Matrix and Gap Analysis

## Purpose

The specification matrix and gap analysis layer turns normalized supplier specifications into decision-ready product development tables.

After the product page connector extracts and normalizes raw specifications, users still need to answer practical questions:

- Which products include power input information?
- Which products lack waterproof ratings?
- Which specification fields are common across competitors?
- Which required fields are missing for a security camera or vehicle camera project?
- Which products need additional supplier confirmation?

The specification matrix module helps answer these questions.

## Input

The module uses normalized specification rows generated from public product pages.

Typical normalized row fields:

```text
source_url
standard_field
standard_label
raw_spec_name
raw_spec_value
normalized_value
confidence
category
parser
fetched_at
```

## Specification Matrix

The Specification Matrix is a product-by-field table.

Example:

| source_url | title | power_input | operating_temperature | waterproof_rating |
|---|---|---|---|---|
| product-a | Vehicle Camera A | DC 10-32V | -20°C to 70°C |  |
| product-b | License Plate Camera | DC 12V | -20°C to 70°C | IP69K |

This table helps product developers compare competing products directly.

## Coverage Summary

The Coverage Summary calculates how often each specification field appears across the product set.

Example:

| standard_field | products_with_value | total_products | coverage_rate |
|---|---:|---:|---:|
| power_input | 2 | 2 | 100% |
| operating_temperature | 2 | 2 | 100% |
| waterproof_rating | 1 | 2 | 50% |
| supports_rtsp | 0 | 2 | 0% |

Use it to identify:

- Common market fields
- Frequently missing fields
- Fields that need more manual verification
- Potential specification gaps in supplier pages

## Required Field Profiles

The first version includes three profiles.

### Generic Hardware

Baseline fields for general hardware research:

```text
power_input
operating_temperature
dimensions
```

### Security Camera

Baseline fields for security camera product definition:

```text
resolution
night_vision_type
waterproof_rating
operating_temperature
wireless_protocol
battery_capacity_mah
supports_rtsp
supports_onvif
```

### Vehicle Camera

Baseline fields for backup cameras, vehicle monitors and vehicle imaging systems:

```text
camera_resolution
monitor_size
power_input
waterproof_rating
operating_temperature
wireless_protocol
latency_ms
transmission_range_m
```

## Gap Analysis

Gap Analysis compares each product against a selected required-field profile.

Output fields:

```text
source_url
title
brand
model
profile
profile_label
missing_fields
missing_labels
missing_count
required_fields_count
completion_rate
risk_level
```

Risk level is based on missing required field count:

| Missing count | Risk level |
|---:|---|
| 0-1 | low |
| 2-3 | medium |
| 4+ | high |

## How to use the results

### Product development

Use Gap Analysis to identify which supplier pages need further confirmation before product definition.

Example:

```text
Missing: latency_ms, transmission_range_m
Action: Ask supplier for latency and wireless range test data.
```

### Supplier communication

Send the missing-field list to suppliers as a structured request.

Example:

```text
Please confirm:
- Waterproof rating
- Operating temperature
- Power input
- Wireless transmission distance
```

### Market research

Use Coverage Summary to identify which fields are consistently disclosed in the market.

High coverage may indicate market-standard parameters. Low coverage may indicate either:

- suppliers do not disclose the field,
- the field is not relevant,
- or the current parser needs improvement.

### Product differentiation

If most competitors do not disclose a field but users care about it, the field may become a communication opportunity.

Example:

```text
Low coverage: latency_ms
Potential action: Test and promote low-latency performance if the product is strong.
```

## Limitations

This module is a rules-based first version.

It does not:

- verify whether supplier data is true,
- replace engineering testing,
- replace certification review,
- generate final product requirements automatically,
- translate raw product titles or raw specification values,
- parse PDF datasheets.

Users should review all results before using them for supplier negotiation, product definition or compliance decisions.

## Future improvements

Planned improvements:

- Better unit extraction and conversion
- Field-specific validation rules
- Product category auto-detection
- Supplier-specific page adapters
- Specification conflict detection
- Specification matrix charts
- Exportable product requirement draft

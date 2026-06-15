# Specification Foundation

## Purpose

The specification foundation converts raw supplier specification names into standard hardware product fields.

For example:

```text
Power Supply → power_input
Operating Temperature → operating_temperature
Waterproof Rating → waterproof_rating
Dimension of Multiplexer Box → dimensions
```

This is the foundation for future specification matrix and gap analysis.

## Current standard fields

The first version includes fields such as:

```text
resolution
camera_resolution
monitor_size
monitor_resolution
power_input
operating_temperature
storage_temperature
waterproof_rating
dimensions
battery_capacity_mah
wireless_protocol
transmission_range_m
latency_ms
night_vision_type
ir_distance_m
supports_rtsp
supports_onvif
field_of_view
anti_vibration
power_consumption
```

## How normalization works

The current version uses alias matching.

Examples:

```text
Power Supply
Power Input
DC Input
供电输入
输入电压
→ power_input
```

```text
Operating Temperature
Working Temperature
工作温度
→ operating_temperature
```

```text
Waterproof
Waterproof Rating
IP Rating
防水等级
→ waterproof_rating
```

## Output fields

The normalized specification output includes:

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

## Important limitation

This is a rules-based first version. It is designed to make raw supplier specs easier to review, not to make final engineering decisions automatically.

Users should review all normalized values before using them for product definition, supplier negotiation or compliance decisions.

## Future improvements

Planned improvements:

- Better unit extraction
- Field-specific value validation
- Security camera specification matrix
- Vehicle imaging specification matrix
- Missing parameter detection
- Conflicting parameter detection
- Supplier-specific adapters

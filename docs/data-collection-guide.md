# Data Collection Guide

## Why templates are needed

Many product teams do not start with clean data. Information is usually scattered across:

- Amazon research spreadsheets
- Third-party tool exports
- Supplier quotes
- Supplier websites
- PDF datasheets
- Internal notes
- Product pages
- Manual comparison tables

The Template Center gives users a structured way to start collecting data without guessing field names.

## Recommended data sources

### Market research data

Use:

- Internal product research spreadsheets
- Third-party tool exports
- Manually collected competitor data
- Publicly available data that the user is allowed to use

Avoid mixing unrelated product categories in one sheet unless you plan to filter later.

### Supplier quotes

Use the supplier quote template to record:

- Supplier name
- Contact
- Product model
- MOQ
- Unit cost
- Sample cost
- Lead time
- Certifications
- App solution
- Firmware ownership
- Private server support

This helps product developers compare not only price, but also technical and cooperation risk.

### Product URLs

Use the product URL template when you want the connector to collect public product page data.

Recommended URLs:

- Supplier product pages
- Brand product pages
- Public static product detail pages

Avoid:

- Amazon product pages
- Login-only pages
- CAPTCHA-protected pages
- Pages that require special access
- Private links

## Template Center files

### Market research template

Use this for competitor and market research data.

Core fields:

```text
asin
title
brand
price
rating
reviews
monthly_sales
category
source
notes
```

### Supplier quote template

Use this for supplier comparison and sourcing.

Core fields:

```text
supplier_name
contact
product_model
moq
unit_cost
sample_cost
lead_time_days
certifications
app_solution
firmware_ownership
private_server_support
notes
```

### Product URL import template

Use this to collect public product page URLs before batch importing.

Core fields:

```text
source_url
brand
category
priority
notes
```

### Security camera specification template

Use this for battery cameras, 4G cameras, Wi-Fi cameras, solar cameras and general security camera projects.

### Vehicle camera specification template

Use this for backup cameras, trailer cameras, vehicle monitors and wireless vehicle imaging systems.

## Best practice

Start with 10 to 30 products, not hundreds.

A small clean dataset is better than a large unclear dataset. After the workflow is validated, scale up to more product pages or more spreadsheet rows.

# Amazon Market Research Dashboard

## What this tool is for

This dashboard is designed for Amazon product developers, ecommerce product managers and hardware sourcing teams who need to turn mixed research data into practical product decisions.

It supports spreadsheet imports, public supplier product page collection, data validation, profit estimation and early-stage hardware specification normalization.

## Key workflows

### 1. Spreadsheet import

Use this workflow when you already have product research data from internal spreadsheets or third-party research tools.

Supported files:

- CSV
- XLSX
- XLS

The dashboard can:

- Select Excel worksheets
- Suggest field mappings
- Validate missing or invalid rows
- Detect duplicate ASINs
- Export normalized workbooks

### 2. Product page connector

Use this workflow when you have public supplier or brand product URLs.

The connector extracts:

- Product title
- Brand and model when available
- JSON-LD Product data
- HTML specification tables
- Document links
- Fetch logs
- Raw and normalized specifications

### 3. Template Center

Use this workflow when you do not yet have a structured data file.

Available templates:

- Market research template
- Supplier quote template
- Product URL import template
- Security camera specification template
- Vehicle camera specification template

Each template includes a data dictionary and example sheet.

## What this tool does not do

This tool does not bypass access restrictions.

It does not:

- Scrape Amazon product pages as a core workflow
- Bypass login pages
- Bypass CAPTCHA
- Access private pages
- Bypass paywalls
- Perform high-frequency crawling

## Recommended first use

1. Open the online demo.
2. Choose Template Center.
3. Download the market research or product URL template.
4. Fill or collect a small sample.
5. Upload the file or paste product URLs.
6. Review issues and normalized results.
7. Export the workbook for team review.

## Local setup

```bash
python -m venv .venv
```

Windows:

```bat
.venv\Scripts\activate
```

Install dependencies and start the app:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

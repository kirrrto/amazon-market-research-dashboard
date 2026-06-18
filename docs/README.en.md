# Amazon Market Research Dashboard

## What this tool is for

This dashboard is designed for Amazon product developers, ecommerce product managers and hardware sourcing teams who need to turn mixed research data into practical product development decisions.

It supports spreadsheet imports, public supplier product page collection, data validation, profit estimation, hardware specification normalization, specification matrix generation, gap analysis, product requirement drafts, supplier follow-up questions, product readiness scoring, supplier comparison and product pool prioritization.

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

### 4. Specification matrix and gap analysis

Use this workflow after product URLs have been collected and specifications have been normalized.

The app can generate:

- Specification Matrix
- Coverage Summary
- Gap Analysis

This helps identify which products include important parameters and which products require follow-up with suppliers.

### 5. Requirement draft and supplier follow-up

Use this workflow after gap analysis.

The app can generate:

- Product Requirement Draft
- Supplier Follow-up Questions
- Decision Summary

These outputs help product developers turn analysis results into actionable supplier and engineering follow-up.

### 6. Readiness score and supplier comparison

Use this workflow when several products or suppliers need to be compared.

The app can generate:

- Product Readiness Summary
- Supplier Comparison
- Product Pool Summary

These outputs help product teams prioritize review candidates, supplier follow-up and risk review items.

## What this tool does not do

This tool does not bypass access restrictions.

It does not:

- Scrape Amazon product pages as a core workflow
- Bypass login pages
- Bypass CAPTCHA
- Access private pages
- Bypass paywalls
- Perform high-frequency crawling
- Verify supplier claims automatically
- Make final product launch decisions

## Recommended first use

1. Open the online demo.
2. Choose Template Center.
3. Download the market research or product URL template.
4. Fill or collect a small sample.
5. Upload the file or paste product URLs.
6. Review issues and normalized results.
7. Review Specification Matrix, Coverage Summary and Gap Analysis.
8. Review Product Requirement Draft, Supplier Follow-up Questions and Decision Summary.
9. Review Product Readiness Summary, Supplier Comparison and Product Pool Summary.
10. Export the workbook for team review.

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

# Amazon Market Research Dashboard

## Language

- [English](docs/README.en.md)
- [简体中文](docs/README.zh-CN.md)

## Live Demo

Try the dashboard online:

[Open Amazon Market Research Dashboard](https://kirrrto-amazon-market-research.streamlit.app)

## Overview

A lightweight product research and market analysis dashboard for Amazon product developers, cross-border ecommerce teams, sourcing teams and hardware product managers.

The project helps users import spreadsheet research data, collect public supplier product page information, validate data quality, estimate profit, normalize hardware specifications, compare specification gaps, and generate product requirement drafts and supplier follow-up questions.

This project does not replace Helium 10, Jungle Scout, Keepa or other specialized data platforms. Instead, it provides a practical workflow layer for turning mixed research data, supplier pages and internal spreadsheets into auditable product development inputs.

## Current Capabilities

### Spreadsheet Import

- Import CSV, XLSX and XLS files
- Select worksheets from multi-sheet Excel workbooks
- Suggest English and Chinese field mappings
- Allow manual field mapping correction
- Detect duplicate ASINs, missing identifiers and invalid numeric values
- Generate row-level validation issues
- Export normalized Products, Issues and Import Report worksheets

### Public Product Page Connector

- Paste public supplier or brand product page URLs
- Fetch public static HTML pages
- Extract JSON-LD Product data when available
- Extract HTML specification tables and definition-list specifications
- Preserve source URL, status code, domain and collection timestamp
- Export Products, Raw Specifications, Normalized Specifications, Specification Matrix, Coverage Summary, Gap Analysis, Product Requirement Draft, Supplier Follow-up Questions, Decision Summary, Fetch Logs and Issues worksheets

See [Public Product Page Connector](docs/product-page-connector.md).

### Template Center

- Download market research template
- Download supplier quote template
- Download product URL import template
- Download security camera specification template
- Download vehicle camera specification template
- Each template includes a data dictionary and example sheet

### Specification Matrix and Gap Analysis

- Initial hardware specification field dictionary
- English and Chinese specification aliases
- Raw supplier specification name mapping
- Product-by-specification matrix
- Field coverage summary
- Required-field gap analysis
- Low / medium / high risk level based on missing required fields

See [Specification Matrix and Gap Analysis](docs/specification-matrix.md).

### Product Requirement Draft and Supplier Follow-up

- Convert specification matrix rows into product requirement draft rows
- Convert missing specification fields into supplier follow-up questions
- Generate product decision summary from gap risk levels
- Support English and Simplified Chinese workbook labels
- Preserve source URL and evidence path for review

See [Product Requirement Draft Export](docs/requirement-draft-export.md).

### Market and Profit Analysis

- Estimated monthly revenue
- Price band distribution
- Brand concentration
- Product opportunity score
- Unit gross profit and net profit
- Net margin
- Break-even price
- Estimated monthly net profit

## Data Source Policy

The project is designed for auditable and user-provided data sources.

Supported sources include:

- Public supplier and brand product pages explicitly provided by users
- User-owned internal research spreadsheets
- CSV / Excel exports from third-party tools
- Manually prepared market research templates
- Future authorized APIs

The project does **not**:

- Scrape Amazon product pages as a core feature
- Bypass login pages
- Bypass CAPTCHA
- Access private pages
- Bypass paywalls or site restrictions
- Perform high-frequency crawling
- Make final legal, compliance or product-launch decisions

## Recommended Workflow

```text
Download template
→ Collect or import data
→ Validate fields
→ Review issues
→ Export normalized workbook
→ Analyze market and profit
→ Collect product URLs
→ Review normalized specs
→ Compare specification matrix
→ Review coverage and gaps
→ Generate requirement draft
→ Send supplier follow-up questions
→ Review decision summary
→ Define next product requirements
```

See [Data Collection Guide](docs/data-collection-guide.md).

## Local Setup

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bat
.venv\Scripts\activate
```

Activate it on macOS / Linux:

```bash
source .venv/bin/activate
```

Install dependencies and start the application:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Run Tests

```bash
python -m pytest -q
```

## Roadmap

- [ ] Product requirement draft refinement
- [ ] Supplier scoring model
- [ ] Compliance matrix
- [ ] PDF datasheet extraction
- [ ] Word / PDF research report export
- [ ] Domain-specific supplier website adapters
- [ ] Browser-assisted data capture
- [ ] Product requirement table export for engineering teams

## License

MIT

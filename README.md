# Amazon Market Research Dashboard

## Language

- [English](docs/README.en.md)
- [简体中文](docs/README.zh-CN.md)

## Live Demo

Try the dashboard online:

[Open Amazon Market Research Dashboard](https://kirrrto-amazon-market-research.streamlit.app)

## Overview

A lightweight product research and product development dashboard for Amazon and cross-border ecommerce teams.

The project helps users import spreadsheet research data, collect public supplier product page information, validate data quality, estimate profit, normalize hardware specifications, compare specification gaps, generate product requirement drafts, create supplier follow-up questions, score product readiness and compare supplier candidates.

This project does not replace Helium 10, Jungle Scout, Keepa, SellerSprite, Sorftime or other specialized commercial data platforms. Instead, it provides a practical workflow layer for turning mixed research data, supplier pages and internal spreadsheets into auditable product development decisions.

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
- Export Products, Raw Specifications, Normalized Specifications, Specification Matrix, Coverage Summary, Gap Analysis, Product Requirement Draft, Supplier Follow-up Questions, Decision Summary, Product Readiness Summary, Supplier Comparison, Product Pool Summary, Fetch Logs and Issues worksheets

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

### Product Readiness Score and Supplier Comparison

- Score product readiness from specification completeness, risk level, metadata completeness, supplier follow-up count and requirement candidate count
- Build Product Readiness Summary rows with score, status, recommendation and next action
- Aggregate product rows into supplier-level comparison metrics
- Generate Product Pool Summary rows for filtering and prioritization
- Support dashboard tabs and workbook exports for product readiness, supplier comparison and product pool review

See [Product Readiness Score and Supplier Comparison](docs/readiness-score-and-supplier-comparison.md).

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
→ Score product readiness
→ Compare suppliers
→ Prioritize product pool
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

- [ ] Supplier quote comparison
- [ ] Compliance matrix
- [ ] Product requirement table export for engineering teams
- [ ] PDF datasheet extraction
- [ ] Word / PDF research report export
- [ ] Domain-specific supplier website adapters
- [ ] Browser-assisted data capture
- [ ] Market opportunity dashboard
- [ ] VOC and review insight workflow

## License

MIT

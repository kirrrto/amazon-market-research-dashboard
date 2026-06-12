# Public Product Page Connector

The public product page connector helps users collect product information from explicitly provided public supplier or brand product pages.

It is designed for product research workflows where manually copying product titles, specifications and document links one by one is inefficient.

## Supported Inputs

The current connector accepts one product page URL per line.

Example:

```text
https://supplier.example.com/products/wireless-backup-camera
https://brand.example.com/products/4g-solar-security-camera
```

## Supported Page Types

The first version is designed for:

- Public supplier product pages
- Public brand product pages
- Static HTML product pages
- Pages containing JSON-LD Product data
- Pages containing HTML specification tables
- Pages containing `<dl><dt><dd>` specification blocks

## Not Supported in This Version

The connector intentionally does not handle:

- Amazon product page HTML scraping
- Login-only pages
- CAPTCHA bypass
- Paywall bypass
- JavaScript-only pages that require a browser runtime
- PDF content extraction
- High-frequency crawling
- Private network or localhost URLs

## Extracted Data

The connector attempts to extract:

| Field | Source |
|---|---|
| `source_url` | User-provided URL |
| `domain` | Parsed URL domain |
| `status` | Fetch and parsing status |
| `status_code` | HTTP response status |
| `title` | JSON-LD, meta tags or HTML title |
| `brand` | JSON-LD Product brand |
| `model` | JSON-LD model, MPN or SKU |
| `price` | JSON-LD offers |
| `image_url` | JSON-LD image, Open Graph image or first image |
| `document_urls` | PDF, Word, Excel, CSV or ZIP links |
| `raw_specs` | JSON-LD additionalProperty, HTML tables and definition lists |
| `fetched_at` | UTC collection timestamp |
| `error_message` | Fetch or parsing issue message |

## Output Workbook

The exported workbook contains four sheets.

### Products

One row per URL, including title, brand, model, price, image URL, document links, parser names and fetch status.

### Raw Specifications

One row per extracted specification.

Columns:

```text
source_url
spec_name
spec_value
parser
fetched_at
```

### Fetch Logs

One row per fetch attempt.

Columns:

```text
source_url
domain
success
status_code
elapsed_ms
fetched_at
error_message
```

### Issues

Warnings and errors generated during URL validation, fetching or parsing.

## Data Quality Notes

This connector extracts available page data. It does not guarantee that extracted values are complete, current or commercially accurate.

Users should review extracted results before using them for supplier negotiation, product definition or financial decisions.

## Access and Compliance Principles

The connector follows these principles:

- Only fetch user-provided public URLs
- Only support HTTP and HTTPS URLs
- Do not bypass login, CAPTCHA or access restrictions
- Keep requests sequential in the initial version
- Preserve source URL and fetch timestamp
- Show clear errors instead of silently dropping failed pages
- Use local HTML fixtures for automated tests instead of live websites

## Recommended Workflow

```text
Paste supplier or brand product URLs
→ Fetch product pages
→ Review Products, Raw Specifications, Fetch Logs and Issues
→ Download Excel
→ Use extracted data as input for specification templates and market analysis
```

## Future Improvements

Planned improvements include:

- Domain-level rate limiting
- `robots.txt` policy checks
- JavaScript-rendered page support through a controlled browser engine
- PDF datasheet parsing
- Specification alias normalization
- Security camera and vehicle camera field templates
- Supplier website monitoring

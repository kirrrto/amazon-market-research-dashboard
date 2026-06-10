# Spreadsheet Import Workflow

The dashboard accepts CSV, XLSX and legacy XLS files through a guided import workflow.

## Steps

1. Upload a file or use the included sample.
2. Select an Excel worksheet when the workbook contains multiple sheets.
3. Preview the first 20 rows.
4. Confirm the automatically suggested field mappings.
5. Validate the data and review row-level errors and warnings.
6. Download a normalized workbook or continue to market analysis.

## Required standard fields

- `asin`
- `title`
- `brand`
- `price`
- `rating`
- `reviews`
- `monthly_sales`
- `category`

## Validation behavior

Rows without an ASIN, rows with invalid required numeric values and duplicate ASIN rows are rejected. Blank brand and category values, negative values and ratings outside 0–5 are reported before normalization.

## Normalized workbook

The exported workbook contains:

- **Products** — cleaned product data
- **Issues** — row number, severity, field, raw value and action message
- **Import Report** — source metadata, counts and field mapping

## Privacy and limits

Uploaded files are processed in memory by the running Streamlit application. The project does not intentionally retain source files. The default project limit is 20 MB and 20,000 data rows per worksheet.

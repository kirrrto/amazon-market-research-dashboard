# Changelog

## Unreleased

- Added product readiness scoring from gap analysis, metadata completeness and supplier follow-up counts
- Added readiness status labels: Ready for Review, Follow-up Required, High Risk and Not Ready
- Added supplier comparison generator with supplier-level readiness, missing-field and follow-up metrics
- Added product pool summary with P1-P4 prioritization
- Added Product Readiness Summary, Supplier Comparison and Product Pool Summary workbook sheets
- Added Streamlit dashboard metrics for average readiness, review candidates, supplier count and follow-up questions
- Added Streamlit tabs for Readiness Score, Supplier Comparison and Product Pool
- Added bilingual labels for readiness, supplier comparison and product pool outputs
- Added documentation for product readiness score and supplier comparison workflows

## 0.5.0

- Added product requirement draft generation from specification matrix and gap risk data
- Added supplier follow-up question generation from missing specification fields
- Added decision summary generation based on gap analysis risk levels
- Added Product Requirement Draft, Supplier Follow-up Questions and Decision Summary sheets to connector exports
- Added Streamlit tabs for requirement draft, supplier follow-up and decision summary
- Added bilingual sheet and column labels for product requirement outputs
- Added documentation for requirement draft and supplier follow-up workflows

## 0.4.0

- Added specification matrix builder
- Added specification coverage summary
- Added required specification profiles for generic hardware, security cameras and vehicle imaging products
- Added missing-field gap analysis with low / medium / high risk levels
- Added Specification Matrix, Coverage Summary and Gap Analysis sheets to product page connector exports
- Added bilingual labels for matrix, coverage and gap analysis exports
- Added Streamlit UI tabs for matrix, coverage and gap analysis
- Added documentation for specification matrix interpretation

## 0.3.0

- Added bilingual translation helpers for English and Simplified Chinese
- Added Template Center workbook generator
- Added downloadable market research, supplier quote, product URL, security camera and vehicle camera templates
- Added hardware specification dictionary and alias-based normalization
- Added Normalized Specifications export for product page connector results
- Added bilingual Streamlit interface basics
- Added localized workbook sheet and column labels
- Added English and Chinese user documentation

## 0.2.0

- Added public product page connector foundation
- Added public URL validation and sequential fetching
- Added JSON-LD Product extraction
- Added HTML specification table and definition-list extraction
- Added source URL, fetch logs, parsing issues and collection timestamps
- Added product page connector Excel export
- Added local HTML fixture tests for connector parsing and export

## 0.1.0

- Added CSV, XLSX and XLS spreadsheet import
- Added worksheet selection and field mapping
- Added row-level validation reporting
- Added normalized Excel workbook export
- Added gross margin and net profit estimation
- Preserved full precision when calculating monthly net profit
- Added currency and percentage formats to exported profit columns
- Added automated tests and GitHub Actions

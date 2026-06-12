from __future__ import annotations

from .html_specs import extract_html_product_data
from .jsonld import extract_jsonld_product_data
from .models import ConnectorIssue, FetchResult, ProductPageRecord
from .web_fetcher import fetch_url


def _first_value(*values: str) -> str:
    for value in values:
        if str(value or "").strip():
            return str(value).strip()
    return ""


def _merge_specs(*spec_lists: list[dict[str, str]]) -> list[dict[str, str]]:
    merged: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()

    for specs in spec_lists:
        for item in specs:
            name = str(item.get("name", "")).strip()
            value = str(item.get("value", "")).strip()
            parser = str(item.get("parser", "")).strip()
            if not name or not value:
                continue

            key = (name.lower(), value.lower(), parser)
            if key in seen:
                continue
            seen.add(key)
            merged.append({"name": name, "value": value, "parser": parser})

    return merged


def parse_product_page(source_url: str, html: str, base_record: ProductPageRecord | None = None) -> ProductPageRecord:
    """Parse a fetched public product page into a ProductPageRecord."""

    record = base_record or ProductPageRecord(source_url=source_url, status="fetched")
    jsonld = extract_jsonld_product_data(html, base_url=source_url)
    html_data = extract_html_product_data(html, base_url=source_url)

    record.title = _first_value(jsonld.get("title", ""), html_data.get("title", ""))
    record.brand = _first_value(jsonld.get("brand", ""), html_data.get("brand", ""))
    record.model = _first_value(jsonld.get("model", ""), html_data.get("model", ""))
    record.price = _first_value(jsonld.get("price", ""), html_data.get("price", ""))
    record.image_url = _first_value(
        jsonld.get("image_url", ""),
        html_data.get("image_url", ""),
    )
    record.document_urls = list(
        dict.fromkeys(
            [
                *record.document_urls,
                *html_data.get("document_urls", []),
            ]
        )
    )
    record.raw_specs = _merge_specs(
        jsonld.get("raw_specs", []),
        html_data.get("raw_specs", []),
    )
    record.parser_names = list(
        dict.fromkeys(
            [
                *record.parser_names,
                *jsonld.get("parser_names", []),
                *html_data.get("parser_names", []),
            ]
        )
    )

    if not record.title and not record.raw_specs:
        record.status = "parsed_with_warnings"
        record.error_message = "No product title or specification data was detected."
    elif record.status == "fetched":
        record.status = "parsed"

    return record


def collect_product_pages(urls: list[str]) -> FetchResult:
    """Fetch and parse product pages from user-provided public URLs."""

    result = FetchResult()
    seen: set[str] = set()

    for raw_url in urls:
        if not str(raw_url).strip():
            continue

        if str(raw_url).strip() in seen:
            result.issues.append(
                ConnectorIssue(
                    source_url=str(raw_url).strip(),
                    severity="warning",
                    error_code="duplicate_url",
                    message="Duplicate URL was skipped.",
                )
            )
            continue
        seen.add(str(raw_url).strip())

        record, log, issue, html = fetch_url(raw_url)
        result.fetch_logs.append(log)

        if issue is not None or not html:
            result.records.append(record)
            if issue is not None:
                result.issues.append(issue)
            continue

        parsed = parse_product_page(record.source_url, html, record)
        result.records.append(parsed)

        if parsed.status == "parsed_with_warnings":
            result.issues.append(
                ConnectorIssue(
                    source_url=parsed.source_url,
                    severity="warning",
                    error_code="no_product_data",
                    message=parsed.error_message,
                )
            )

    return result

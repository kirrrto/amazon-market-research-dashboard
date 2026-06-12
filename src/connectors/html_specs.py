from __future__ import annotations

import re
from html import unescape
from html.parser import HTMLParser
from typing import Any
from urllib.parse import urljoin


DOCUMENT_EXTENSIONS = (
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".csv",
    ".zip",
)


def _clean_text(value: str) -> str:
    text = unescape(value or "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


class _ProductHtmlParser(HTMLParser):
    def __init__(self, base_url: str = "") -> None:
        super().__init__(convert_charrefs=True)
        self.base_url = base_url

        self._title_active = False
        self._title_parts: list[str] = []
        self.meta: dict[str, str] = {}

        self._current_table: list[list[str]] | None = None
        self._current_row: list[str] | None = None
        self._current_cell_parts: list[str] | None = None
        self._inside_cell = False
        self.tables: list[list[list[str]]] = []

        self._current_dt: str | None = None
        self._dt_active = False
        self._dd_active = False
        self._definition_parts: list[str] = []
        self.definition_specs: list[dict[str, str]] = []

        self.document_urls: list[str] = []
        self.image_urls: list[str] = []

    @property
    def page_title(self) -> str:
        return _clean_text(" ".join(self._title_parts))

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        attributes = {name.lower(): value or "" for name, value in attrs}

        if tag == "title":
            self._title_active = True

        elif tag == "meta":
            key = (
                attributes.get("property")
                or attributes.get("name")
                or attributes.get("itemprop")
            )
            content = attributes.get("content", "")
            if key and content:
                self.meta[key.lower()] = _clean_text(content)

        elif tag == "table":
            self._current_table = []

        elif tag == "tr" and self._current_table is not None:
            self._current_row = []

        elif tag in {"td", "th"} and self._current_row is not None:
            self._inside_cell = True
            self._current_cell_parts = []

        elif tag == "dt":
            self._dt_active = True
            self._definition_parts = []

        elif tag == "dd":
            self._dd_active = True
            self._definition_parts = []

        elif tag == "a":
            href = attributes.get("href", "")
            if href and href.lower().split("?", 1)[0].endswith(DOCUMENT_EXTENSIONS):
                self.document_urls.append(urljoin(self.base_url, href))

        elif tag == "img":
            src = attributes.get("src") or attributes.get("data-src") or ""
            if src:
                self.image_urls.append(urljoin(self.base_url, src))

    def handle_data(self, data: str) -> None:
        if self._title_active:
            self._title_parts.append(data)

        if self._inside_cell and self._current_cell_parts is not None:
            self._current_cell_parts.append(data)

        if self._dt_active or self._dd_active:
            self._definition_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()

        if tag == "title":
            self._title_active = False

        elif tag in {"td", "th"} and self._inside_cell:
            if self._current_row is not None and self._current_cell_parts is not None:
                self._current_row.append(_clean_text(" ".join(self._current_cell_parts)))
            self._inside_cell = False
            self._current_cell_parts = None

        elif tag == "tr" and self._current_row is not None:
            if self._current_table is not None and any(self._current_row):
                self._current_table.append(self._current_row)
            self._current_row = None

        elif tag == "table" and self._current_table is not None:
            if self._current_table:
                self.tables.append(self._current_table)
            self._current_table = None

        elif tag == "dt":
            self._current_dt = _clean_text(" ".join(self._definition_parts))
            self._dt_active = False
            self._definition_parts = []

        elif tag == "dd":
            value = _clean_text(" ".join(self._definition_parts))
            if self._current_dt and value:
                self.definition_specs.append(
                    {
                        "name": self._current_dt,
                        "value": value,
                        "parser": "html.dl",
                    }
                )
            self._dd_active = False
            self._definition_parts = []


def _extract_table_specs(tables: list[list[list[str]]]) -> list[dict[str, str]]:
    specs: list[dict[str, str]] = []
    for table in tables:
        for row in table:
            cells = [cell for cell in row if cell]
            if len(cells) < 2:
                continue

            # Skip common table headers.
            first = cells[0].lower()
            second = cells[1].lower()
            if first in {"specification", "spec", "parameter", "item", "name"} and second in {
                "value",
                "description",
                "details",
            }:
                continue

            name, value = cells[0], cells[1]
            if name and value and len(name) <= 120 and len(value) <= 500:
                specs.append(
                    {
                        "name": name,
                        "value": value,
                        "parser": "html.table",
                    }
                )
    return specs


def extract_html_product_data(html: str, base_url: str = "") -> dict[str, Any]:
    """Extract basic product fields and raw specification tables from HTML."""

    parser = _ProductHtmlParser(base_url=base_url)
    parser.feed(html)

    title = (
        parser.meta.get("og:title")
        or parser.meta.get("twitter:title")
        or parser.meta.get("title")
        or parser.page_title
    )
    description = parser.meta.get("description", "")
    image_url = (
        parser.meta.get("og:image")
        or parser.meta.get("twitter:image")
        or (parser.image_urls[0] if parser.image_urls else "")
    )
    if image_url:
        image_url = urljoin(base_url, image_url)

    raw_specs = _extract_table_specs(parser.tables)
    raw_specs.extend(parser.definition_specs)

    return {
        "title": title,
        "brand": "",
        "model": "",
        "price": "",
        "image_url": image_url,
        "description": description,
        "document_urls": list(dict.fromkeys(parser.document_urls)),
        "raw_specs": raw_specs,
        "parser_names": ["html.meta", "html.table"] if raw_specs else ["html.meta"],
    }

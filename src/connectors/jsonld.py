from __future__ import annotations

import json
import re
from html import unescape
from html.parser import HTMLParser
from typing import Any
from urllib.parse import urljoin


class _JsonLdScriptParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._inside_jsonld = False
        self._buffer: list[str] = []
        self.scripts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "script":
            return
        attributes = {name.lower(): value or "" for name, value in attrs}
        script_type = attributes.get("type", "").lower()
        if script_type == "application/ld+json":
            self._inside_jsonld = True
            self._buffer = []

    def handle_data(self, data: str) -> None:
        if self._inside_jsonld:
            self._buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "script" and self._inside_jsonld:
            content = "".join(self._buffer).strip()
            if content:
                self.scripts.append(unescape(content))
            self._inside_jsonld = False
            self._buffer = []


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _node_type(node: dict[str, Any]) -> set[str]:
    raw_type = node.get("@type", "")
    values = _as_list(raw_type)
    return {str(item).lower() for item in values}


def _walk_jsonld(value: Any) -> list[dict[str, Any]]:
    nodes: list[dict[str, Any]] = []

    if isinstance(value, dict):
        nodes.append(value)
        for key, child in value.items():
            if key in {"@graph", "itemListElement", "mainEntity", "mainEntityOfPage"}:
                nodes.extend(_walk_jsonld(child))
            elif isinstance(child, (dict, list)):
                nodes.extend(_walk_jsonld(child))

    elif isinstance(value, list):
        for item in value:
            nodes.extend(_walk_jsonld(item))

    return nodes


def _load_jsonld_scripts(html: str) -> list[Any]:
    parser = _JsonLdScriptParser()
    parser.feed(html)

    values: list[Any] = []
    for script in parser.scripts:
        cleaned = script.strip()
        cleaned = re.sub(r"^<!--", "", cleaned).strip()
        cleaned = re.sub(r"-->$", "", cleaned).strip()

        try:
            values.append(json.loads(cleaned))
        except json.JSONDecodeError:
            # Some pages contain multiple JSON-LD objects separated by newlines.
            for line in cleaned.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    values.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    return values


def _string_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, dict):
        for key in ("name", "value", "text", "@id"):
            if key in value:
                return _string_value(value.get(key))
    if isinstance(value, list):
        for item in value:
            text = _string_value(item)
            if text:
                return text
    return ""


def _extract_brand(value: Any) -> str:
    return _string_value(value)


def _extract_price(offers: Any) -> str:
    for offer in _as_list(offers):
        if not isinstance(offer, dict):
            continue
        for key in ("price", "lowPrice", "highPrice"):
            text = _string_value(offer.get(key))
            if text:
                currency = _string_value(offer.get("priceCurrency"))
                return f"{currency} {text}".strip()
    return ""


def _extract_image(value: Any, base_url: str) -> str:
    image = _string_value(value)
    return urljoin(base_url, image) if image else ""


def _extract_additional_properties(node: dict[str, Any]) -> list[dict[str, str]]:
    specs: list[dict[str, str]] = []
    for prop in _as_list(node.get("additionalProperty")):
        if not isinstance(prop, dict):
            continue
        name = _string_value(prop.get("name") or prop.get("propertyID"))
        value = _string_value(prop.get("value"))
        if name and value:
            specs.append(
                {
                    "name": name,
                    "value": value,
                    "parser": "jsonld.additionalProperty",
                }
            )
    return specs


def extract_jsonld_product_data(html: str, base_url: str = "") -> dict[str, Any]:
    """Extract Product data from JSON-LD blocks in a public product page."""

    product_nodes: list[dict[str, Any]] = []
    for value in _load_jsonld_scripts(html):
        for node in _walk_jsonld(value):
            if isinstance(node, dict) and "product" in _node_type(node):
                product_nodes.append(node)

    if not product_nodes:
        return {
            "title": "",
            "brand": "",
            "model": "",
            "price": "",
            "image_url": "",
            "raw_specs": [],
            "parser_names": [],
        }

    # Prefer the richest Product node.
    node = max(product_nodes, key=lambda item: len(item))
    title = _string_value(node.get("name"))
    brand = _extract_brand(node.get("brand"))
    model = _string_value(node.get("model") or node.get("mpn") or node.get("sku"))
    price = _extract_price(node.get("offers"))
    image_url = _extract_image(node.get("image"), base_url)
    raw_specs = _extract_additional_properties(node)

    return {
        "title": title,
        "brand": brand,
        "model": model,
        "price": price,
        "image_url": image_url,
        "raw_specs": raw_specs,
        "parser_names": ["jsonld.product"],
    }

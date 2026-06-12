from pathlib import Path

from src.connectors.html_specs import extract_html_product_data
from src.connectors.jsonld import extract_jsonld_product_data
from src.connectors.product_page import parse_product_page
from src.connectors.models import ProductPageRecord

FIXTURES = Path(__file__).parent / "fixtures" / "product_pages"


def read_fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def test_extract_jsonld_product_data():
    data = extract_jsonld_product_data(
        read_fixture("jsonld_product.html"),
        base_url="https://supplier.example.com/products/sh-4g-200",
    )

    assert data["title"] == "4G Solar Security Camera"
    assert data["brand"] == "SecureHome"
    assert data["model"] == "SH-4G-200"
    assert data["price"] == "USD 129.99"
    assert data["image_url"] == "https://supplier.example.com/images/sh-4g-200.jpg"
    assert {item["name"] for item in data["raw_specs"]} == {
        "Resolution",
        "Waterproof Rating",
    }
    assert "jsonld.product" in data["parser_names"]


def test_extract_html_specification_tables_and_document_links():
    data = extract_html_product_data(
        read_fixture("html_specs.html"),
        base_url="https://brand.example.com/products/backup-camera",
    )

    assert data["title"] == "Wireless Backup Camera Kit"
    assert data["image_url"] == "https://brand.example.com/assets/camera-kit.jpg"
    assert data["document_urls"] == [
        "https://brand.example.com/docs/backup-camera-datasheet.pdf"
    ]
    specs = {(item["name"], item["value"]) for item in data["raw_specs"]}
    assert ("Resolution", "1080P") in specs
    assert ("Wireless Range", "100m open area") in specs
    assert ("Waterproof", "IP69K") in specs
    assert ("Operating Temperature", "-20°C to 70°C") in specs


def test_parse_product_page_merges_jsonld_and_html_specs():
    html = read_fixture("jsonld_product.html") + read_fixture("html_specs.html")
    record = parse_product_page(
        "https://supplier.example.com/products/camera",
        html,
        ProductPageRecord(source_url="https://supplier.example.com/products/camera", status="fetched"),
    )

    assert record.status == "parsed"
    assert record.title == "4G Solar Security Camera"
    assert record.brand == "SecureHome"
    assert record.price == "USD 129.99"
    spec_names = {item["name"] for item in record.raw_specs}
    assert {"Resolution", "Waterproof Rating", "Wireless Range"}.issubset(spec_names)
    assert "jsonld.product" in record.parser_names
    assert "html.table" in record.parser_names


def test_parse_product_page_reports_warning_when_no_product_data():
    record = parse_product_page(
        "https://supplier.example.com/about",
        read_fixture("empty_product.html"),
        ProductPageRecord(source_url="https://supplier.example.com/about", status="fetched"),
    )

    assert record.status == "parsed"
    assert record.title == "About us"
    assert record.raw_specs == []

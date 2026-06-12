"""Public product page connector services.

The connector package is responsible for collecting product information from
explicitly provided public URLs and converting fetch results into auditable
records. It does not bypass authentication, CAPTCHA, paywalls or other access
controls.
"""

from .html_specs import extract_html_product_data
from .jsonld import extract_jsonld_product_data
from .models import ConnectorIssue, FetchLog, FetchResult, ProductPageRecord
from .product_page import collect_product_pages, parse_product_page
from .web_fetcher import (
    DEFAULT_TIMEOUT_SECONDS,
    WebFetchError,
    fetch_url,
    fetch_urls,
    normalize_url,
    validate_public_url,
)

__all__ = [
    "ConnectorIssue",
    "FetchLog",
    "FetchResult",
    "ProductPageRecord",
    "DEFAULT_TIMEOUT_SECONDS",
    "WebFetchError",
    "collect_product_pages",
    "extract_html_product_data",
    "extract_jsonld_product_data",
    "fetch_url",
    "fetch_urls",
    "normalize_url",
    "parse_product_page",
    "validate_public_url",
]

"""Public product page connector services.

The connector package is responsible for collecting product information from
explicitly provided public URLs and converting fetch results into auditable
records. It does not bypass authentication, CAPTCHA, paywalls or other access
controls.
"""

from .models import ConnectorIssue, FetchLog, FetchResult, ProductPageRecord
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
    "fetch_url",
    "fetch_urls",
    "normalize_url",
    "validate_public_url",
]

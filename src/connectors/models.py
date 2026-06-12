from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

import pandas as pd


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class ConnectorIssue:
    source_url: str
    severity: str
    error_code: str
    message: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "source_url": self.source_url,
            "severity": self.severity,
            "error_code": self.error_code,
            "message": self.message,
        }


@dataclass(frozen=True)
class FetchLog:
    source_url: str
    domain: str
    success: bool
    status_code: int | None
    elapsed_ms: int
    fetched_at: datetime = field(default_factory=utc_now)
    error_message: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "source_url": self.source_url,
            "domain": self.domain,
            "success": self.success,
            "status_code": self.status_code,
            "elapsed_ms": self.elapsed_ms,
            "fetched_at": self.fetched_at.isoformat(timespec="seconds"),
            "error_message": self.error_message,
        }


@dataclass
class ProductPageRecord:
    source_url: str
    fetched_at: datetime = field(default_factory=utc_now)
    status: str = "pending"
    status_code: int | None = None
    title: str = ""
    brand: str = ""
    model: str = ""
    price: str = ""
    image_url: str = ""
    document_urls: list[str] = field(default_factory=list)
    raw_specs: list[dict[str, str]] = field(default_factory=list)
    parser_names: list[str] = field(default_factory=list)
    error_message: str = ""

    @property
    def domain(self) -> str:
        return urlparse(self.source_url).netloc.lower()

    def product_row(self) -> dict[str, Any]:
        return {
            "source_url": self.source_url,
            "domain": self.domain,
            "status": self.status,
            "status_code": self.status_code,
            "title": self.title,
            "brand": self.brand,
            "model": self.model,
            "price": self.price,
            "image_url": self.image_url,
            "document_urls": "\n".join(self.document_urls),
            "parser_names": ", ".join(dict.fromkeys(self.parser_names)),
            "fetched_at": self.fetched_at.isoformat(timespec="seconds"),
            "error_message": self.error_message,
        }

    def specs_rows(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for item in self.raw_specs:
            rows.append(
                {
                    "source_url": self.source_url,
                    "spec_name": str(item.get("name", "")),
                    "spec_value": str(item.get("value", "")),
                    "parser": str(item.get("parser", "")),
                    "fetched_at": self.fetched_at.isoformat(timespec="seconds"),
                }
            )
        return rows


@dataclass
class FetchResult:
    records: list[ProductPageRecord] = field(default_factory=list)
    fetch_logs: list[FetchLog] = field(default_factory=list)
    issues: list[ConnectorIssue] = field(default_factory=list)

    @property
    def products_frame(self) -> pd.DataFrame:
        columns = [
            "source_url",
            "domain",
            "status",
            "status_code",
            "title",
            "brand",
            "model",
            "price",
            "image_url",
            "document_urls",
            "parser_names",
            "fetched_at",
            "error_message",
        ]
        if not self.records:
            return pd.DataFrame(columns=columns)
        return pd.DataFrame(
            [record.product_row() for record in self.records],
            columns=columns,
        )

    @property
    def raw_specs_frame(self) -> pd.DataFrame:
        columns = ["source_url", "spec_name", "spec_value", "parser", "fetched_at"]
        rows: list[dict[str, Any]] = []
        for record in self.records:
            rows.extend(record.specs_rows())
        if not rows:
            return pd.DataFrame(columns=columns)
        return pd.DataFrame(rows, columns=columns)

    @property
    def fetch_logs_frame(self) -> pd.DataFrame:
        columns = [
            "source_url",
            "domain",
            "success",
            "status_code",
            "elapsed_ms",
            "fetched_at",
            "error_message",
        ]
        if not self.fetch_logs:
            return pd.DataFrame(columns=columns)
        return pd.DataFrame(
            [log.as_dict() for log in self.fetch_logs],
            columns=columns,
        )

    @property
    def issues_frame(self) -> pd.DataFrame:
        columns = ["source_url", "severity", "error_code", "message"]
        if not self.issues:
            return pd.DataFrame(columns=columns)
        return pd.DataFrame(
            [issue.as_dict() for issue in self.issues],
            columns=columns,
        )

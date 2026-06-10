from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class ImportIssue:
    row_number: int | None
    severity: str
    field: str
    error_code: str
    raw_value: Any
    message: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "row_number": self.row_number,
            "severity": self.severity,
            "field": self.field,
            "error_code": self.error_code,
            "raw_value": "" if self.raw_value is None else str(self.raw_value),
            "message": self.message,
        }


@dataclass(frozen=True)
class ImportReport:
    source_file: str
    worksheet: str | None
    original_rows: int
    valid_rows: int
    rejected_rows: int
    warning_rows: int
    duplicate_asins: int
    mapping: dict[str, str]
    imported_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def summary_rows(self) -> list[tuple[str, Any]]:
        return [
            ("Source file", self.source_file),
            ("Worksheet", self.worksheet or "CSV"),
            ("Imported at (UTC)", self.imported_at.isoformat(timespec="seconds")),
            ("Original rows", self.original_rows),
            ("Valid rows", self.valid_rows),
            ("Rejected rows", self.rejected_rows),
            ("Warning rows", self.warning_rows),
            ("Duplicate ASINs", self.duplicate_asins),
        ]


@dataclass
class ImportResult:
    products: pd.DataFrame
    issues: list[ImportIssue]
    report: ImportReport

    @property
    def issues_frame(self) -> pd.DataFrame:
        columns = [
            "row_number",
            "severity",
            "field",
            "error_code",
            "raw_value",
            "message",
        ]
        if not self.issues:
            return pd.DataFrame(columns=columns)
        return pd.DataFrame([issue.as_dict() for issue in self.issues], columns=columns)

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class RequirementDraftRow:
    """A product requirement draft row derived from a specification matrix."""

    source_url: str
    title: str
    brand: str
    model: str
    profile: str
    risk_level: str
    requirement_field: str
    requirement_label: str
    current_value: str
    evidence_source: str
    action: str
    notes: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

"""Hardware specification field dictionary and analysis helpers."""

from .aliases import find_standard_field, normalize_alias_key
from .coverage import build_coverage_summary
from .fields import SpecificationField, get_spec_field, list_spec_fields
from .gaps import build_gap_analysis, risk_level_for_missing_count
from .matrix import build_specification_matrix, matrix_field_columns
from .normalizer import normalize_raw_specifications, normalize_spec_value
from .profiles import SpecProfile, get_spec_profile, list_spec_profiles

__all__ = [
    "SpecProfile",
    "SpecificationField",
    "build_coverage_summary",
    "build_gap_analysis",
    "build_specification_matrix",
    "find_standard_field",
    "get_spec_field",
    "get_spec_profile",
    "list_spec_fields",
    "list_spec_profiles",
    "matrix_field_columns",
    "normalize_alias_key",
    "normalize_raw_specifications",
    "normalize_spec_value",
    "risk_level_for_missing_count",
]

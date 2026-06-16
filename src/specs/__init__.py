"""Hardware specification field dictionary and analysis helpers."""

from .aliases import find_standard_field, normalize_alias_key
from .fields import SpecificationField, get_spec_field, list_spec_fields
from .matrix import build_specification_matrix, matrix_field_columns
from .normalizer import normalize_raw_specifications, normalize_spec_value

__all__ = [
    "SpecificationField",
    "build_specification_matrix",
    "find_standard_field",
    "get_spec_field",
    "list_spec_fields",
    "matrix_field_columns",
    "normalize_alias_key",
    "normalize_raw_specifications",
    "normalize_spec_value",
]

"""Hardware specification field dictionary and normalization helpers."""

from .aliases import find_standard_field, normalize_alias_key
from .fields import SpecificationField, get_spec_field, list_spec_fields
from .normalizer import normalize_raw_specifications, normalize_spec_value

__all__ = [
    "SpecificationField",
    "find_standard_field",
    "get_spec_field",
    "list_spec_fields",
    "normalize_alias_key",
    "normalize_raw_specifications",
    "normalize_spec_value",
]

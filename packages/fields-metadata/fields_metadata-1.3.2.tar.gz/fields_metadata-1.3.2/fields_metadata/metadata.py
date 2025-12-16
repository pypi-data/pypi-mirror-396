"""Field metadata dataclass definition."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FieldMetadata:
    """
    Metadata information for a field.

    :param field_name: The name of the field
    :param field_type: The type of the field (e.g., list, str, int)
    :param items_type: For multivalued fields, the type of items; None otherwise
    :param effective_type: items_type for multivalued fields, field_type otherwise
    :param multivalued: True if field is a collection (list, tuple, set, etc.)
    :param composite: True if effective_type is a composite (dataclass, BaseModel)
    :param parent_field: Field path of the parent field for nested fields (e.g., 'address' for 'address.street')
    :param numeric: True if field is numeric (excluding bool)
    :param computed: True if field is computed (property, computed_field)
    :param derived: True if field is derived from another field via hooks
    :param optional: True if field type is Union with None
    :param categorical: True if field is categorical (False for float, datetime, timedelta, composite, or NonCategorical)
    :param final: True if field has no non-derived subfields (primitives or composite types marked as final)
    :param original_annotation: The original field type annotation (with Annotated, Union, etc.)
    :param doc: Documentation from DocInfo annotation
    :param classification: Dictionary with classification metadata
    :param extra: Dictionary for additional metadata
    """

    field_name: str
    field_type: type[Any]
    items_type: type[Any] | None = None
    effective_type: type[Any] | None = None
    multivalued: bool = False
    composite: bool = False
    parent_field: str | None = None
    numeric: bool = False
    computed: bool = False
    derived: bool = False
    optional: bool = False
    categorical: bool = True
    final: bool = True
    original_annotation: type[Any] | None = None
    doc: str | None = None
    classification: dict[str, Any] = field(default_factory=dict)
    extra: dict[str, Any] = field(default_factory=dict)


__all__ = [
    "FieldMetadata",
]

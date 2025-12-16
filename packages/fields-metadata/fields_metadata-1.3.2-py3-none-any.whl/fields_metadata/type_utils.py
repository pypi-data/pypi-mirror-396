"""Type detection and analysis utilities."""

import dataclasses
import typing
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import Any, cast, get_args, get_origin

from fields_metadata.exceptions import InvalidTypeUnionError, NoneTypeFieldError


def get_origin_and_args(type_hint: type[Any]) -> tuple[Any, tuple[Any, ...]]:
    """
    Get origin and args from a type hint.

    :param type_hint: The type hint to analyze
    :return: Tuple of (origin, args)
    """
    origin = get_origin(type_hint)
    args = get_args(type_hint)
    return origin, args


def unwrap_annotated(type_hint: type[Any]) -> type[Any]:
    """
    Recursively unwrap Annotated types from a type hint.

    This handles both direct Annotated types and Annotated types nested
    within generic types like list[Annotated[int, ...]].

    Examples:
        Annotated[int, ...] -> int
        list[Annotated[int, ...]] -> list[int]
        dict[str, Annotated[int, ...]] -> dict[str, int]
        Annotated[list[str], ...] -> list[str]

    :param type_hint: The type hint to unwrap
    :return: The unwrapped type hint
    """
    origin = get_origin(type_hint)

    if origin is typing.Annotated:
        args = get_args(type_hint)
        if args:
            return unwrap_annotated(cast(type[Any], args[0]))
        return type_hint

    if origin is not None:
        args = get_args(type_hint)
        if args:
            unwrapped_args = tuple(unwrap_annotated(cast(type[Any], arg)) for arg in args)
            try:
                return origin[unwrapped_args]  # type: ignore[no-any-return]
            except (TypeError, AttributeError):
                return type_hint

    return type_hint


def is_multivalued_type(type_hint: type[Any]) -> bool:
    """
    Check if a type is a collection (list, tuple, set, frozenset, etc.).

    :param type_hint: The type to check
    :return: True if the type is a multivalued collection, False otherwise
    """
    origin, _ = get_origin_and_args(type_hint)
    if origin is None:
        return False

    multivalued_types = (list, tuple, set, frozenset)
    return origin in multivalued_types


def get_items_type(type_hint: type[Any]) -> type[Any] | None:
    """
    Extract the item type from a collection type.

    If the item type is Annotated, it will be unwrapped to the base type.

    :param type_hint: The collection type to analyze
    :return: The type of items in the collection, or None if not a collection
    """
    if not is_multivalued_type(type_hint):
        return None

    _, args = get_origin_and_args(type_hint)
    if not args:
        return None

    item_type = cast(type[Any], args[0])

    if get_origin(item_type) is typing.Annotated:
        unwrapped_args = get_args(item_type)
        if unwrapped_args:
            return cast(type[Any], unwrapped_args[0])

    return item_type


def is_optional_type(type_hint: type[Any]) -> tuple[bool, type[Any] | None]:
    """
    Check if type is Optional/Union with None.

    :param type_hint: The type to check
    :return: Tuple of (is_optional, non_none_type). If not optional, returns (False, None)
    :raises InvalidTypeUnionError: If union has multiple non-None types
    :raises NoneTypeFieldError: If type is only None
    """
    if type_hint is type(None) or type_hint is None:
        raise NoneTypeFieldError("Field cannot have only None as its type")

    origin, args = get_origin_and_args(type_hint)

    if origin is None:
        return False, None

    try:
        from types import UnionType

        is_union = origin is UnionType
    except ImportError:
        is_union = False

    if not is_union:
        is_union = origin is typing.Union

    if not is_union:
        return False, None

    none_count = sum(1 for arg in args if arg is type(None))
    non_none_types = [arg for arg in args if arg is not type(None)]

    if none_count == 0:
        raise InvalidTypeUnionError(
            f"Union with multiple non-None types is not supported: {type_hint}"
        )

    if len(non_none_types) == 0:
        raise NoneTypeFieldError("Field cannot have only None as its type")

    if len(non_none_types) > 1:
        raise InvalidTypeUnionError(
            f"Union with multiple non-None types is not supported: {type_hint}"
        )

    return True, non_none_types[0]


def validate_type_union(type_hint: type[Any]) -> None:
    """
    Validate that unions are only with None.

    :param type_hint: The type to validate
    :raises InvalidTypeUnionError: If union has multiple non-None types
    :raises NoneTypeFieldError: If type is only None
    """
    is_optional_type(type_hint)


def is_composite_type(type_hint: type[Any]) -> bool:
    """
    Check if a type is composite (dataclass or pydantic BaseModel).

    :param type_hint: The type to check
    :return: True if the type is a dataclass or pydantic BaseModel, False otherwise
    """
    if dataclasses.is_dataclass(type_hint):
        return True

    try:
        from pydantic import BaseModel

        return isinstance(type_hint, type) and issubclass(type_hint, BaseModel)
    except ImportError:
        return False


def is_numeric_type(type_hint: type[Any]) -> bool:
    """
    Check if type is numeric (int, float, Decimal, date, datetime, time, timedelta).

    Excludes bool even though it's technically an int subclass.

    :param type_hint: The type to check
    :return: True if the type is numeric (excluding bool), False otherwise
    """
    if type_hint is bool:
        return False

    numeric_types = (int, float, Decimal, datetime, date, time, timedelta)

    try:
        return isinstance(type_hint, type) and issubclass(type_hint, numeric_types)
    except TypeError:
        return False


def is_computed_field(obj_class: type[Any], field_name: str) -> bool:
    """
    Check if a field is computed (property or pydantic computed_field).

    :param obj_class: The class containing the field
    :param field_name: The name of the field to check
    :return: True if the field is computed, False otherwise
    """
    if hasattr(obj_class, field_name):
        attr = getattr(obj_class, field_name)
        if isinstance(attr, property):
            return True

    try:
        computed_fields = getattr(obj_class, "__pydantic_computed_fields__", {})
        return field_name in computed_fields
    except Exception:
        return False


def is_non_categorical_type(type_hint: type[Any]) -> bool:
    """
    Check if type is inherently non-categorical (float, datetime, timedelta).

    These types are considered non-categorical because they represent continuous
    values or temporal data rather than discrete categories.

    :param type_hint: The type to check
    :return: True if the type is non-categorical, False otherwise
    """
    non_categorical_types = (float, datetime, timedelta)

    try:
        return isinstance(type_hint, type) and issubclass(type_hint, non_categorical_types)
    except TypeError:
        return False


def extract_annotations_from_type(type_hint: type[Any]) -> list[Any]:
    """
    Extract annotations from Annotated types.

    :param type_hint: The type hint to analyze
    :return: List of annotations (empty list if not Annotated)
    """
    origin, args = get_origin_and_args(type_hint)

    if origin is not typing.Annotated:
        return []

    if len(args) < 2:
        return []

    return list(args[1:])


__all__ = [
    "get_origin_and_args",
    "unwrap_annotated",
    "is_multivalued_type",
    "get_items_type",
    "is_optional_type",
    "validate_type_union",
    "is_composite_type",
    "is_numeric_type",
    "is_computed_field",
    "is_non_categorical_type",
    "extract_annotations_from_type",
]

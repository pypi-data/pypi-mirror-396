"""Tests for type utility functions."""

from contextlib import nullcontext as does_not_raise
from dataclasses import dataclass
from datetime import date, datetime, time
from decimal import Decimal
from typing import Annotated, Any

import pytest

from fields_metadata.exceptions import InvalidTypeUnionError, NoneTypeFieldError
from fields_metadata.type_utils import (
    extract_annotations_from_type,
    get_items_type,
    get_origin_and_args,
    is_composite_type,
    is_computed_field,
    is_multivalued_type,
    is_numeric_type,
    is_optional_type,
    unwrap_annotated,
    validate_type_union,
)


@pytest.mark.parametrize(
    "type_hint,expected",
    [
        (list[str], True),
        (tuple[int, ...], True),
        (set[float], True),
        (frozenset[str], True),
        (str, False),
        (int, False),
        (dict[str, int], False),
    ],
)
def test_is_multivalued_type(type_hint: type, expected: bool) -> None:
    """Test multivalued type detection."""
    assert is_multivalued_type(type_hint) == expected


@pytest.mark.parametrize(
    "type_hint,expected",
    [
        (list[str], str),
        (tuple[int, ...], int),
        (set[float], float),
        (frozenset[bool], bool),
        (str, None),
        (int, None),
    ],
)
def test_get_items_type(type_hint: type, expected: type | None) -> None:
    """Test extraction of item types from collections."""
    assert get_items_type(type_hint) == expected


def test_get_items_type_unwraps_annotated() -> None:
    """Test that get_items_type unwraps Annotated item types."""
    from annotated_types import Ge, Le

    # For list[Annotated[int, ...]], items_type should be unwrapped to int
    type_hint = list[Annotated[int, Ge(0), Le(100)]]
    assert get_items_type(type_hint) == int

    # For set[Annotated[str, ...]], items_type should be unwrapped to str
    from annotated_types import MinLen

    type_hint_set = set[Annotated[str, MinLen(5)]]
    assert get_items_type(type_hint_set) == str


@pytest.mark.parametrize(
    "type_hint,expected_optional,expected_type,expectation",
    [
        (str | None, True, str, does_not_raise()),
        (int | None, True, int, does_not_raise()),
        (list[str] | None, True, list[str], does_not_raise()),
        (str, False, None, does_not_raise()),
        (int, False, None, does_not_raise()),
        (str | int, None, None, pytest.raises(InvalidTypeUnionError)),
        (str | int | None, None, None, pytest.raises(InvalidTypeUnionError)),
        (type(None), None, None, pytest.raises(NoneTypeFieldError)),
    ],
)
def test_is_optional_type(
    type_hint: type,
    expected_optional: bool | None,
    expected_type: type | None,
    expectation: Any,
) -> None:
    """Test optional type detection and validation."""
    with expectation:
        is_optional, non_none_type = is_optional_type(type_hint)
        if expected_optional is not None:
            assert is_optional == expected_optional
            assert non_none_type == expected_type


@pytest.mark.parametrize(
    "type_hint,expectation",
    [
        (str, does_not_raise()),
        (int, does_not_raise()),
        (str | None, does_not_raise()),
        (int | None, does_not_raise()),
        (str | int, pytest.raises(InvalidTypeUnionError)),
        (str | int | float, pytest.raises(InvalidTypeUnionError)),
        (type(None), pytest.raises(NoneTypeFieldError)),
    ],
)
def test_validate_type_union(type_hint: type, expectation: Any) -> None:
    """Test type union validation."""
    with expectation:
        validate_type_union(type_hint)


def test_is_composite_type_with_dataclass() -> None:
    """Test composite type detection with dataclass."""

    @dataclass
    class TestClass:
        field: str

    assert is_composite_type(TestClass) is True


def test_is_composite_type_with_regular_class() -> None:
    """Test composite type detection with regular class."""

    class TestClass:
        field: str

    assert is_composite_type(TestClass) is False


def test_is_composite_type_with_primitive() -> None:
    """Test composite type detection with primitive types."""
    assert is_composite_type(str) is False
    assert is_composite_type(int) is False
    assert is_composite_type(list) is False


@pytest.mark.parametrize(
    "type_hint,expected",
    [
        (int, True),
        (float, True),
        (Decimal, True),
        (datetime, True),
        (date, True),
        (time, True),
        (bool, False),
        (str, False),
        (list, False),
    ],
)
def test_is_numeric_type(type_hint: type, expected: bool) -> None:
    """Test numeric type detection."""
    assert is_numeric_type(type_hint) == expected


def test_is_computed_field_with_property() -> None:
    """Test computed field detection with property."""

    class TestClass:
        @property
        def computed_field(self) -> str:
            return "computed"

    assert is_computed_field(TestClass, "computed_field") is True


def test_is_computed_field_with_regular_field() -> None:
    """Test computed field detection with regular field."""

    @dataclass
    class TestClass:
        regular_field: str

    assert is_computed_field(TestClass, "regular_field") is False


def test_is_computed_field_with_nonexistent_field() -> None:
    """Test computed field detection with nonexistent field."""

    @dataclass
    class TestClass:
        field: str

    assert is_computed_field(TestClass, "nonexistent") is False


def test_extract_annotations_from_annotated_type() -> None:
    """Test extraction of annotations from Annotated type."""
    from annotated_types import MinLen

    type_hint = Annotated[str, MinLen(5), "doc"]
    annotations = extract_annotations_from_type(type_hint)

    assert len(annotations) == 2
    assert isinstance(annotations[0], MinLen)
    assert annotations[1] == "doc"


def test_extract_annotations_from_non_annotated_type() -> None:
    """Test extraction from non-Annotated type returns empty list."""
    annotations = extract_annotations_from_type(str)
    assert annotations == []


def test_get_origin_and_args_with_generic() -> None:
    """Test get_origin_and_args with generic type."""
    origin, args = get_origin_and_args(list[str])
    assert origin == list
    assert args == (str,)


def test_get_origin_and_args_with_non_generic() -> None:
    """Test get_origin_and_args with non-generic type."""
    origin, args = get_origin_and_args(str)
    assert origin is None
    assert args == ()


def test_get_origin_and_args_with_union() -> None:
    """Test get_origin_and_args with Union type."""
    from typing import Union

    origin, args = get_origin_and_args(Union[str, int])
    assert origin == Union
    assert str in args and int in args


def test_unwrap_annotated_simple() -> None:
    """Test unwrapping simple Annotated type."""
    from annotated_types import Ge

    annotated_type = Annotated[int, Ge(0)]
    assert unwrap_annotated(annotated_type) == int


def test_unwrap_annotated_in_list() -> None:
    """Test unwrapping Annotated type inside list."""
    from annotated_types import Ge, Le

    annotated_type = list[Annotated[int, Ge(0), Le(100)]]
    unwrapped = unwrap_annotated(annotated_type)
    assert unwrapped == list[int]


def test_unwrap_annotated_in_set() -> None:
    """Test unwrapping Annotated type inside set."""
    from annotated_types import MinLen

    annotated_type = set[Annotated[str, MinLen(5)]]
    unwrapped = unwrap_annotated(annotated_type)
    assert unwrapped == set[str]


def test_unwrap_annotated_in_tuple() -> None:
    """Test unwrapping Annotated type inside tuple."""
    from annotated_types import MaxLen

    annotated_type = tuple[Annotated[str, MaxLen(10)], ...]
    unwrapped = unwrap_annotated(annotated_type)
    assert unwrapped == tuple[str, ...]


def test_unwrap_annotated_nested() -> None:
    """Test unwrapping nested Annotated types."""
    from annotated_types import MinLen

    # Annotated wrapping a list
    annotated_type = Annotated[list[str], MinLen(1)]
    unwrapped = unwrap_annotated(annotated_type)
    assert unwrapped == list[str]


def test_unwrap_annotated_no_annotation() -> None:
    """Test that non-Annotated types pass through unchanged."""
    assert unwrap_annotated(int) == int
    assert unwrap_annotated(str) == str
    assert unwrap_annotated(list[str]) == list[str]
    assert unwrap_annotated(dict[str, int]) == dict[str, int]


def test_unwrap_annotated_complex() -> None:
    """Test unwrapping complex nested Annotated types."""
    from annotated_types import Ge, MinLen

    # list[Annotated[list[Annotated[int, Ge(0)]], MinLen(1)]]
    inner = Annotated[int, Ge(0)]
    middle = Annotated[list[inner], MinLen(1)]
    outer = list[middle]

    unwrapped = unwrap_annotated(outer)
    assert unwrapped == list[list[int]]

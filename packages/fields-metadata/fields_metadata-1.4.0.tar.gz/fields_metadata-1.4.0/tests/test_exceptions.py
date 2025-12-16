"""Tests for custom exception classes."""

import pytest

from fields_metadata.exceptions import (
    FieldMetadataError,
    InvalidTypeUnionError,
    NoneTypeFieldError,
)


def test_field_metadata_error_is_exception() -> None:
    """FieldMetadataError should be an Exception subclass."""
    assert issubclass(FieldMetadataError, Exception)


def test_invalid_type_union_error_is_field_metadata_error() -> None:
    """InvalidTypeUnionError should be a FieldMetadataError subclass."""
    assert issubclass(InvalidTypeUnionError, FieldMetadataError)


def test_none_type_field_error_is_field_metadata_error() -> None:
    """NoneTypeFieldError should be a FieldMetadataError subclass."""
    assert issubclass(NoneTypeFieldError, FieldMetadataError)


def test_field_metadata_error_can_be_raised() -> None:
    """FieldMetadataError can be raised and caught."""
    with pytest.raises(FieldMetadataError, match="test message"):
        raise FieldMetadataError("test message")


def test_invalid_type_union_error_can_be_raised() -> None:
    """InvalidTypeUnionError can be raised and caught."""
    with pytest.raises(InvalidTypeUnionError, match="test union error"):
        raise InvalidTypeUnionError("test union error")


def test_none_type_field_error_can_be_raised() -> None:
    """NoneTypeFieldError can be raised and caught."""
    with pytest.raises(NoneTypeFieldError, match="test none error"):
        raise NoneTypeFieldError("test none error")


def test_invalid_type_union_error_caught_as_field_metadata_error() -> None:
    """InvalidTypeUnionError can be caught as FieldMetadataError."""
    with pytest.raises(FieldMetadataError):
        raise InvalidTypeUnionError("test")


def test_none_type_field_error_caught_as_field_metadata_error() -> None:
    """NoneTypeFieldError can be caught as FieldMetadataError."""
    with pytest.raises(FieldMetadataError):
        raise NoneTypeFieldError("test")

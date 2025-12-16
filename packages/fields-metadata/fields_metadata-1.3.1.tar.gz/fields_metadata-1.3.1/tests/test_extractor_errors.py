"""Tests for error handling in extraction."""

import pytest

from fields_metadata.exceptions import InvalidTypeUnionError, NoneTypeFieldError
from fields_metadata.extractor import MetadataExtractor
from tests.fixtures.dataclass_models import InvalidUnionDataclass, NoneOnlyDataclass


def test_invalid_union_raises_error() -> None:
    """Test that invalid union (multiple non-None types) raises error."""
    extractor = MetadataExtractor()

    with pytest.raises(InvalidTypeUnionError):
        extractor.extract(InvalidUnionDataclass)


def test_none_only_field_raises_error() -> None:
    """Test that None-only field raises error."""
    extractor = MetadataExtractor()

    with pytest.raises(NoneTypeFieldError):
        extractor.extract(NoneOnlyDataclass)


def test_invalid_union_error_message() -> None:
    """Test that invalid union error has descriptive message."""
    extractor = MetadataExtractor()

    with pytest.raises(InvalidTypeUnionError, match="multiple non-None types"):
        extractor.extract(InvalidUnionDataclass)


def test_none_only_error_message() -> None:
    """Test that None-only error has descriptive message."""
    extractor = MetadataExtractor()

    with pytest.raises(NoneTypeFieldError, match="only None"):
        extractor.extract(NoneOnlyDataclass)

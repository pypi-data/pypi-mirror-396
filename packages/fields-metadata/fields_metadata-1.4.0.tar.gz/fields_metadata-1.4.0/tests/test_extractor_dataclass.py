"""Tests for dataclass-specific extraction features."""

from fields_metadata.extractor import MetadataExtractor
from tests.fixtures.dataclass_models import DataclassWithProperty, SimpleDataclass


def test_extract_from_dataclass() -> None:
    """Test that extraction works with standard dataclass."""
    extractor = MetadataExtractor()
    result = extractor.extract(SimpleDataclass)

    assert len(result) > 0
    assert all(isinstance(key, str) for key in result.keys())


def test_dataclass_fields_extracted() -> None:
    """Test that all dataclass fields are extracted."""
    extractor = MetadataExtractor()
    result = extractor.extract(SimpleDataclass)

    field_names = {metadata.field_name for metadata in result.values()}
    assert "name" in field_names
    assert "age" in field_names
    assert "active" in field_names


def test_property_in_extraction() -> None:
    """Test that properties (computed fields) are included in extraction."""
    extractor = MetadataExtractor()
    result = extractor.extract(DataclassWithProperty)

    assert "first_name" in result
    assert "last_name" in result
    # Properties should now be included as computed fields
    assert "full_name" in result
    assert result["full_name"].computed is True
    assert result["full_name"].field_type == str

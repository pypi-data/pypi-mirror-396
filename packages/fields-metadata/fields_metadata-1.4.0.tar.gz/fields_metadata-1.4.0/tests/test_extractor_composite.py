"""Tests for composite and nested field extraction."""

from fields_metadata.extractor import MetadataExtractor
from tests.fixtures.dataclass_models import (
    DataclassWithList,
    DeepNestedDataclass,
    NestedDataclass,
)


def test_extract_nested_dataclass() -> None:
    """Test extraction of nested dataclass fields."""
    extractor = MetadataExtractor()
    result = extractor.extract(NestedDataclass)

    assert len(result) == 5

    assert "name" in result
    assert "address" in result
    assert "address.street" in result
    assert "address.city" in result
    assert "address.postal_code" in result


def test_nested_field_paths() -> None:
    """Test that nested field paths are correctly used as dictionary keys."""
    extractor = MetadataExtractor()
    result = extractor.extract(NestedDataclass)

    # Field paths are the keys in the result dictionary
    assert "address" in result
    assert "address.street" in result
    assert "address.city" in result
    assert "address.postal_code" in result


def test_nested_field_names() -> None:
    """Test that nested field names are correct."""
    extractor = MetadataExtractor()
    result = extractor.extract(NestedDataclass)

    assert result["address"].field_name == "address"
    assert result["address.street"].field_name == "street"
    assert result["address.city"].field_name == "city"
    assert result["address.postal_code"].field_name == "postal_code"


def test_parent_field_relationships() -> None:
    """Test that parent-child relationships are maintained."""
    extractor = MetadataExtractor()
    result = extractor.extract(NestedDataclass)

    assert result["address"].parent_field is None

    assert result["address.street"].parent_field is not None
    assert result["address.street"].parent_field == "address"

    assert result["address.city"].parent_field is not None
    assert result["address.city"].parent_field == "address"


def test_composite_field_flag() -> None:
    """Test that composite field flag is set correctly."""
    extractor = MetadataExtractor()
    result = extractor.extract(NestedDataclass)

    assert result["address"].composite is True

    assert result["address.street"].composite is False
    assert result["address.city"].composite is False


def test_nested_optional_dataclass() -> None:
    """Test extraction of optional nested dataclass."""
    extractor = MetadataExtractor()
    result = extractor.extract(DeepNestedDataclass)

    assert result["address"].optional is True
    assert result["address"].composite is True

    assert "address.street" in result
    assert "address.city" in result
    assert "address.postal_code" in result


def test_list_of_composite_objects() -> None:
    """Test extraction of list containing composite objects."""
    extractor = MetadataExtractor()
    result = extractor.extract(DataclassWithList)

    assert result["addresses"].multivalued is True
    assert result["addresses"].composite is True
    assert result["addresses"].effective_type is not None

    assert "addresses.street" in result
    assert "addresses.city" in result
    assert "addresses.postal_code" in result


def test_list_of_composite_parent_relationships() -> None:
    """Test parent relationships for list of composite objects."""
    extractor = MetadataExtractor()
    result = extractor.extract(DataclassWithList)

    assert result["addresses.street"].parent_field is not None
    assert result["addresses.street"].parent_field == "addresses"
    assert result["addresses"].multivalued is True


def test_nested_field_types() -> None:
    """Test that nested field types are correct."""
    extractor = MetadataExtractor()
    result = extractor.extract(NestedDataclass)

    assert result["address.street"].field_type == str
    assert result["address.city"].field_type == str
    assert result["address.postal_code"].field_type == str


def test_effective_type_for_nested_fields() -> None:
    """Test effective_type for nested composite fields."""
    extractor = MetadataExtractor()
    result = extractor.extract(NestedDataclass)

    assert result["name"].effective_type == str
    assert result["address"].effective_type is not None
    assert result["address.street"].effective_type == str

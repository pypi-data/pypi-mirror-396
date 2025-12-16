"""Tests for basic extraction functionality."""

from fields_metadata.extractor import MetadataExtractor
from tests.fixtures.dataclass_models import (
    DataclassWithList,
    DataclassWithNumericTypes,
    DataclassWithOptional,
    SimpleDataclass,
)


def test_extract_simple_dataclass() -> None:
    """Test extraction from simple dataclass."""
    extractor = MetadataExtractor()
    result = extractor.extract(SimpleDataclass)

    assert len(result) == 3
    assert "name" in result
    assert "age" in result
    assert "active" in result

    assert result["name"].field_name == "name"
    assert result["name"].field_type == str
    assert result["name"].multivalued is False
    assert result["name"].optional is False
    assert result["name"].composite is False

    assert result["age"].field_type == int
    assert result["age"].numeric is True

    assert result["active"].field_type == bool
    assert result["active"].numeric is False


def test_extract_with_optional_fields() -> None:
    """Test extraction of optional fields."""
    extractor = MetadataExtractor()
    result = extractor.extract(DataclassWithOptional)

    assert len(result) == 3

    assert result["name"].optional is False
    assert result["email"].optional is True
    assert result["phone"].optional is True

    assert result["email"].field_type == str
    assert result["phone"].field_type == str


def test_extract_field_paths() -> None:
    """Test that field paths are correctly used as dictionary keys."""
    extractor = MetadataExtractor()
    result = extractor.extract(SimpleDataclass)

    # Field paths are the keys in the result dictionary
    assert "name" in result
    assert "age" in result
    assert "active" in result

    # Verify field names match
    assert result["name"].field_name == "name"
    assert result["age"].field_name == "age"
    assert result["active"].field_name == "active"


def test_extract_numeric_types() -> None:
    """Test detection of numeric types."""
    extractor = MetadataExtractor()
    result = extractor.extract(DataclassWithNumericTypes)

    assert result["age"].numeric is True
    assert result["height"].numeric is True
    assert result["is_active"].numeric is False


def test_extract_multivalued_fields() -> None:
    """Test extraction of multivalued fields."""
    extractor = MetadataExtractor()
    result = extractor.extract(DataclassWithList)

    assert result["tags"].multivalued is True
    assert result["tags"].items_type == str
    assert result["tags"].effective_type == str
    assert result["tags"].field_type == list

    assert result["scores"].multivalued is True
    assert result["scores"].items_type == int
    assert result["scores"].effective_type == int
    assert result["scores"].field_type == list


def test_extract_parent_field_is_none_for_root() -> None:
    """Test that root level fields have no parent."""
    extractor = MetadataExtractor()
    result = extractor.extract(SimpleDataclass)

    assert result["name"].parent_field is None
    assert result["age"].parent_field is None
    assert result["active"].parent_field is None


def test_extract_classification_default_empty() -> None:
    """Test that classification is empty by default."""
    extractor = MetadataExtractor()
    result = extractor.extract(SimpleDataclass)

    assert result["name"].classification == {}
    assert result["age"].classification == {}


def test_extract_extra_default_empty() -> None:
    """Test that extra is empty by default."""
    extractor = MetadataExtractor()
    result = extractor.extract(SimpleDataclass)

    assert result["name"].extra == {}
    assert result["age"].extra == {}


def test_extract_computed_false_by_default() -> None:
    """Test that computed is False for regular fields."""
    extractor = MetadataExtractor()
    result = extractor.extract(SimpleDataclass)

    assert result["name"].computed is False
    assert result["age"].computed is False

"""Tests for annotation extraction."""

from fields_metadata.extractor import MetadataExtractor
from tests.fixtures.dataclass_models import (
    Article,
    Company,
    DataclassWithAnnotations,
    DataclassWithSemantic,
)


def test_extract_doc_annotation() -> None:
    """Test extraction of DocInfo annotation."""
    extractor = MetadataExtractor()
    result = extractor.extract(DataclassWithAnnotations)

    assert result["name"].doc == "Person's full name"


def test_extract_human_readable_id_annotation() -> None:
    """Test extraction of HumanReadableId annotation."""
    extractor = MetadataExtractor()
    result = extractor.extract(DataclassWithAnnotations)

    assert result["name"].extra.get("human_readable_id") is True


def test_extract_multiline_annotation() -> None:
    """Test extraction of Multiline annotation."""
    extractor = MetadataExtractor()
    result = extractor.extract(DataclassWithAnnotations)

    assert result["bio"].extra.get("multiline") is True


def test_extract_ge_le_annotations() -> None:
    """Test extraction of Ge and Le annotations."""
    extractor = MetadataExtractor()
    result = extractor.extract(DataclassWithAnnotations)

    assert result["age"].extra.get("min_value") == 0
    assert result["age"].extra.get("max_value") == 150


def test_extract_min_max_len_annotations() -> None:
    """Test extraction of MinLen and MaxLen annotations."""
    extractor = MetadataExtractor()
    result = extractor.extract(DataclassWithAnnotations)

    assert result["tags"].extra.get("min_length") == 1
    assert result["tags"].extra.get("max_length") == 10


def test_extract_semantic_classification() -> None:
    """Test extraction of SemanticClassification annotation."""
    extractor = MetadataExtractor()
    result = extractor.extract(DataclassWithSemantic)

    assert result["person_name"].classification.get("semantic") == "person_name"
    assert result["email"].classification.get("semantic") == "email"


def test_multiple_annotations_on_same_field() -> None:
    """Test that multiple annotations can be extracted from same field."""
    extractor = MetadataExtractor()
    result = extractor.extract(DataclassWithAnnotations)

    assert result["name"].doc is not None
    assert result["name"].extra.get("human_readable_id") is True

    assert result["age"].extra.get("min_value") is not None
    assert result["age"].extra.get("max_value") is not None


def test_annotations_with_optional_fields() -> None:
    """Test annotation extraction from optional fields."""
    extractor = MetadataExtractor()
    result = extractor.extract(DataclassWithAnnotations)

    assert result["bio"].optional is True
    assert result["bio"].extra.get("multiline") is True

    assert result["tags"].optional is True
    assert result["tags"].extra.get("min_length") == 1
    assert result["tags"].extra.get("max_length") == 10


def test_human_readable_id_updates_parent_field() -> None:
    """Test that HumanReadableId updates parent field with suggested_human_sorting_field."""
    extractor = MetadataExtractor()
    result = extractor.extract(Article)

    # The author.name field should have human_readable_id set
    assert result["author.name"].extra.get("human_readable_id") is True

    # The parent field (author) should have suggested_human_sorting_field set to full path
    assert result["author"].extra.get("suggested_human_sorting_field") == "author.name"


def test_human_readable_id_without_parent() -> None:
    """Test that HumanReadableId on root field doesn't cause errors."""
    extractor = MetadataExtractor()
    result = extractor.extract(DataclassWithAnnotations)

    # The name field (at root level) should have human_readable_id set
    assert result["name"].extra.get("human_readable_id") is True

    # Since it's at root level, there's no parent to update
    # Just verify it doesn't crash and the field works as expected
    assert result["name"].parent_field is None


def test_human_readable_id_with_deep_nesting() -> None:
    """Test that HumanReadableId with deep nesting uses full path from root."""
    extractor = MetadataExtractor()
    result = extractor.extract(Company)

    # The deeply nested building_id field should have human_readable_id set
    assert result["department.location.building_id"].extra.get("human_readable_id") is True

    # The immediate parent field (department.location) should have suggested_human_sorting_field
    # set to the full path "department.location.building_id" (can be used as lookup key)
    assert (
        result["department.location"].extra.get("suggested_human_sorting_field")
        == "department.location.building_id"
    )

    # Verify that department.location.building_id has the correct parent
    assert result["department.location.building_id"].parent_field == "department.location"

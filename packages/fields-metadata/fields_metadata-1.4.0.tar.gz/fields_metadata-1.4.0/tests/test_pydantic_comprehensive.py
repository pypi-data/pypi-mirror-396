"""Comprehensive tests for Pydantic model annotation extraction."""

import uuid
from typing import Annotated

from annotated_types import DocInfo, Ge, Le, MaxLen, MinLen
from pydantic import BaseModel

from fields_metadata.annotations import HumanReadableId, Multiline, SemanticClassification
from fields_metadata.extractor import MetadataExtractor


class PydanticBasicAnnotations(BaseModel):
    """Test basic annotation patterns with Pydantic."""

    # Simple types with Annotated
    name: Annotated[str, DocInfo("Person's name")]
    age: Annotated[int, Ge(0), Le(150), DocInfo("Age in years")]
    score: Annotated[float, Ge(0.0), Le(100.0)]

    # UUID field (the reported issue)
    id: Annotated[uuid.UUID, DocInfo("Unique identifier")]


class PydanticOptionalAnnotations(BaseModel):
    """Test optional fields with Annotated."""

    # Optional with Annotated
    email: Annotated[str, DocInfo("Email address")] | None = None
    bio: Annotated[str, Multiline(), DocInfo("Biography")] | None = None

    # Simple optional
    phone: str | None = None


class PydanticMultivaluedAnnotations(BaseModel):
    """Test multivalued fields with Annotated."""

    # List with outer Annotated
    tags: Annotated[list[str], MinLen(1), MaxLen(10), DocInfo("Tags")]

    # List with inner Annotated
    scores: list[Annotated[int, Ge(0), Le(100)]]

    # Optional list with outer Annotated
    categories: Annotated[list[str], MinLen(1), DocInfo("Categories")] | None = None


class PydanticCustomAnnotations(BaseModel):
    """Test custom annotation types."""

    username: Annotated[str, HumanReadableId(), DocInfo("Username")]
    person_name: Annotated[str, SemanticClassification("person_name")]
    email: Annotated[str, SemanticClassification("email")]


class PydanticComplexNested(BaseModel):
    """Test complex nested annotation patterns."""

    metadata: (
        Annotated[
            list[Annotated[str, MinLen(1)]], MinLen(1), MaxLen(100), DocInfo("Metadata items")
        ]
        | None
    ) = None

    config: Annotated[Annotated[str, MinLen(1)], MaxLen(1000), DocInfo("Configuration string")]


def test_pydantic_basic_annotations():
    """Test basic annotation extraction from Pydantic models."""
    extractor = MetadataExtractor()
    metadata = extractor.extract(PydanticBasicAnnotations)

    assert "name" in metadata
    assert metadata["name"].doc == "Person's name"
    assert metadata["name"].field_type == str

    assert "age" in metadata
    assert metadata["age"].doc == "Age in years"
    assert metadata["age"].extra.get("min_value") == 0
    assert metadata["age"].extra.get("max_value") == 150

    assert "score" in metadata
    assert metadata["score"].extra.get("min_value") == 0.0
    assert metadata["score"].extra.get("max_value") == 100.0


def test_pydantic_uuid_annotation():
    """Test UUID field with Annotated (the reported issue)."""
    extractor = MetadataExtractor()
    metadata = extractor.extract(PydanticBasicAnnotations)

    assert "id" in metadata
    assert metadata["id"].field_type == uuid.UUID
    assert metadata["id"].doc == "Unique identifier"
    # Verify original annotation is preserved
    assert "Annotated" in str(metadata["id"].original_annotation)


def test_pydantic_optional_annotations():
    """Test optional fields with Annotated."""
    extractor = MetadataExtractor()
    metadata = extractor.extract(PydanticOptionalAnnotations)

    assert metadata["email"].optional is True
    assert metadata["email"].doc == "Email address"

    assert metadata["bio"].optional is True
    assert metadata["bio"].doc == "Biography"
    assert metadata["bio"].extra.get("multiline") is True

    assert metadata["phone"].optional is True


def test_pydantic_multivalued_annotations():
    """Test multivalued fields with Annotated."""
    extractor = MetadataExtractor()
    metadata = extractor.extract(PydanticMultivaluedAnnotations)

    # List with outer Annotated
    assert metadata["tags"].multivalued is True
    assert metadata["tags"].field_type == list
    assert metadata["tags"].items_type == str
    assert metadata["tags"].doc == "Tags"
    assert metadata["tags"].extra.get("min_length") == 1
    assert metadata["tags"].extra.get("max_length") == 10

    # List with inner Annotated (annotations not extracted from items)
    assert metadata["scores"].multivalued is True
    assert metadata["scores"].field_type == list
    assert metadata["scores"].items_type == int

    # Optional list with outer Annotated
    assert metadata["categories"].multivalued is True
    assert metadata["categories"].optional is True
    assert metadata["categories"].doc == "Categories"
    assert metadata["categories"].extra.get("min_length") == 1


def test_pydantic_custom_annotations():
    """Test custom annotation types with Pydantic."""
    extractor = MetadataExtractor()
    metadata = extractor.extract(PydanticCustomAnnotations)

    assert metadata["username"].extra.get("human_readable_id") is True
    assert metadata["username"].doc == "Username"

    assert metadata["person_name"].classification.get("semantic") == "person_name"
    assert metadata["email"].classification.get("semantic") == "email"


def test_pydantic_complex_nested():
    """Test complex nested annotation patterns."""
    extractor = MetadataExtractor()
    metadata = extractor.extract(PydanticComplexNested)

    assert metadata["metadata"].multivalued is True
    assert metadata["metadata"].optional is True
    assert metadata["metadata"].doc == "Metadata items"
    assert metadata["metadata"].extra.get("min_length") == 1
    assert metadata["metadata"].extra.get("max_length") == 100

    assert metadata["config"].doc == "Configuration string"
    assert metadata["config"].extra.get("min_length") == 1
    assert metadata["config"].extra.get("max_length") == 1000


def test_pydantic_original_annotation_preserved():
    """Test that original_annotation is correctly preserved for Pydantic."""
    extractor = MetadataExtractor()
    metadata = extractor.extract(PydanticBasicAnnotations)

    # Annotated fields should have original annotation preserved
    assert "Annotated" in str(metadata["name"].original_annotation)
    assert "DocInfo" in str(metadata["name"].original_annotation)

    # UUID field specifically
    assert "Annotated" in str(metadata["id"].original_annotation)
    assert "uuid.UUID" in str(metadata["id"].original_annotation)


def test_pydantic_vs_dataclass_consistency():
    """Test that Pydantic models behave consistently with dataclasses."""
    from dataclasses import dataclass

    @dataclass
    class DataclassModel:
        name: Annotated[str, DocInfo("Name")]
        age: Annotated[int, Ge(0)]
        tags: Annotated[list[str], MinLen(1)]

    class PydanticModel(BaseModel):
        name: Annotated[str, DocInfo("Name")]
        age: Annotated[int, Ge(0)]
        tags: Annotated[list[str], MinLen(1)]

    extractor = MetadataExtractor()
    dc_metadata = extractor.extract(DataclassModel)
    py_metadata = extractor.extract(PydanticModel)

    # Compare key attributes
    for field in ["name", "age", "tags"]:
        assert dc_metadata[field].field_type == py_metadata[field].field_type
        assert dc_metadata[field].doc == py_metadata[field].doc
        assert dc_metadata[field].extra == py_metadata[field].extra
        assert dc_metadata[field].multivalued == py_metadata[field].multivalued

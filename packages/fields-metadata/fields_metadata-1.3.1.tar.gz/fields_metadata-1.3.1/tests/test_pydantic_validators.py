"""Tests for Pydantic models and dataclasses with Annotated types and validators."""

import dataclasses
from typing import Annotated

from annotated_types import Ge, Le, MaxLen, MinLen
from pydantic import AfterValidator, BaseModel, BeforeValidator

from fields_metadata.extractor import MetadataExtractor


def validate_positive(v: int) -> int:
    """Validator function to ensure value is positive."""
    if v <= 0:
        raise ValueError("must be positive")
    return v


def validate_uppercase(v: str) -> str:
    """Validator function to ensure value is uppercase."""
    return v.upper()


class PydanticWithAfterValidator(BaseModel):
    """Pydantic model with AfterValidator."""

    name: Annotated[str, AfterValidator(validate_uppercase)]
    age: Annotated[int, AfterValidator(validate_positive)]
    description: str


class PydanticWithBeforeValidator(BaseModel):
    """Pydantic model with BeforeValidator."""

    email: Annotated[str, BeforeValidator(lambda v: v.lower())]
    score: Annotated[int, BeforeValidator(lambda v: max(0, v))]


class PydanticWithMultipleAnnotations(BaseModel):
    """Pydantic model with multiple annotations including validators."""

    name: Annotated[str, MinLen(5), AfterValidator(validate_uppercase), MaxLen(100)]
    age: Annotated[int, Ge(0), AfterValidator(validate_positive), Le(150)]


@dataclasses.dataclass
class DataclassWithAnnotatedValidators:
    """Dataclass with Annotated fields (using annotated-types)."""

    name: Annotated[str, MinLen(5), MaxLen(100)]
    age: Annotated[int, Ge(0), Le(150)]
    description: str


@dataclasses.dataclass
class DataclassWithOptionalAnnotated:
    """Dataclass with optional Annotated fields."""

    name: Annotated[str, MinLen(5)]
    bio: Annotated[str | None, MinLen(10)] = None
    tags: list[str] | None = None


@dataclasses.dataclass
class DataclassWithNestedAnnotated:
    """Dataclass with nested Annotated types."""

    tags: Annotated[list[str], MinLen(1), MaxLen(10)]
    scores: list[Annotated[int, Ge(0), Le(100)]]


def test_pydantic_field_type_unwraps_annotated_with_after_validator():
    """Test that field_type is the unwrapped type, not Annotated (AfterValidator)."""
    extractor = MetadataExtractor()
    metadata = extractor.extract(PydanticWithAfterValidator)

    # Check that field_type is the actual type, not Annotated
    assert metadata["name"].field_type == str
    assert metadata["age"].field_type == int
    assert metadata["description"].field_type == str


def test_pydantic_field_type_unwraps_annotated_with_before_validator():
    """Test that field_type is the unwrapped type with BeforeValidator."""
    extractor = MetadataExtractor()
    metadata = extractor.extract(PydanticWithBeforeValidator)

    assert metadata["email"].field_type == str
    assert metadata["score"].field_type == int


def test_pydantic_field_type_unwraps_annotated_with_multiple_annotations():
    """Test that field_type is unwrapped even with multiple annotations.

    Note: Pydantic processes annotations itself, so they won't appear in our
    metadata.extra. The important thing is that field_type is correctly unwrapped.
    """
    extractor = MetadataExtractor()
    metadata = extractor.extract(PydanticWithMultipleAnnotations)

    # field_type should be the base type, not Annotated
    assert metadata["name"].field_type == str
    assert metadata["age"].field_type == int

    # Pydantic processes these annotations internally, so we don't extract them


def test_pydantic_optional_field_with_validator():
    """Test optional fields with validators."""

    class ModelWithOptionalValidator(BaseModel):
        name: Annotated[str | None, AfterValidator(lambda v: v.upper() if v else None)] = None
        age: int

    extractor = MetadataExtractor()
    metadata = extractor.extract(ModelWithOptionalValidator)

    assert metadata["name"].field_type == str
    assert metadata["name"].optional is True
    assert metadata["age"].field_type == int


def test_dataclass_field_type_unwraps_annotated():
    """Test that dataclass field_type is the unwrapped type, not Annotated."""
    extractor = MetadataExtractor()
    metadata = extractor.extract(DataclassWithAnnotatedValidators)

    # Check that field_type is the actual type, not Annotated
    assert metadata["name"].field_type == str
    assert metadata["age"].field_type == int
    assert metadata["description"].field_type == str

    # But the annotations should still be processed
    assert metadata["name"].extra["min_length"] == 5
    assert metadata["name"].extra["max_length"] == 100
    assert metadata["age"].extra["min_value"] == 0
    assert metadata["age"].extra["max_value"] == 150


def test_dataclass_optional_annotated_field_type():
    """Test that optional Annotated fields have correct field_type."""
    extractor = MetadataExtractor()
    metadata = extractor.extract(DataclassWithOptionalAnnotated)

    # field_type should be the unwrapped base type
    assert metadata["name"].field_type == str
    assert metadata["name"].optional is False
    assert metadata["name"].extra["min_length"] == 5

    # Optional Annotated field
    assert metadata["bio"].field_type == str
    assert metadata["bio"].optional is True
    assert metadata["bio"].extra["min_length"] == 10

    # Regular optional field - multivalued types use container class only
    assert metadata["tags"].field_type == list
    assert metadata["tags"].items_type == str
    assert metadata["tags"].optional is True


def test_dataclass_nested_annotated_types():
    """Test that nested Annotated types are handled correctly."""
    extractor = MetadataExtractor()
    metadata = extractor.extract(DataclassWithNestedAnnotated)

    # For Annotated[list[str], ...], field_type is just the container class
    assert metadata["tags"].field_type == list
    assert metadata["tags"].items_type == str
    assert metadata["tags"].multivalued is True
    assert metadata["tags"].extra["min_length"] == 1
    assert metadata["tags"].extra["max_length"] == 10

    # For list[Annotated[int, ...]], field_type is container and items_type is unwrapped
    assert metadata["scores"].field_type == list
    assert metadata["scores"].items_type == int
    assert metadata["scores"].multivalued is True

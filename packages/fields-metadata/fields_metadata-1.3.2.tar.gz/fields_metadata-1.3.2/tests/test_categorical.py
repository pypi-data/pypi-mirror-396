"""Tests for categorical field detection."""

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Annotated

from pydantic import BaseModel

from fields_metadata.annotations import NonCategorical
from fields_metadata.extractor import MetadataExtractor


@dataclass
class CategoricalDataclass:
    """Test categorical field detection in dataclasses."""

    # Categorical fields (default)
    name: str
    age: int
    status: bool
    category: str
    count: int
    uuid_field: uuid.UUID

    # Non-categorical fields (inherent types)
    price: float
    timestamp: datetime
    duration: timedelta

    # Explicitly non-categorical
    score: Annotated[int, NonCategorical()]
    rating: Annotated[str, NonCategorical()]


@dataclass
class Address:
    """Composite type for testing."""

    street: str
    city: str


@dataclass
class PersonWithComposite:
    """Test categorical with composite fields."""

    name: str  # Categorical
    age: int  # Categorical
    address: Address  # Non-categorical (composite)


class CategoricalPydantic(BaseModel):
    """Test categorical field detection in Pydantic models."""

    # Categorical fields
    name: str
    age: int
    is_active: bool

    # Non-categorical fields
    price: float
    created_at: datetime
    duration: timedelta

    # Explicitly non-categorical
    score: Annotated[int, NonCategorical()]


def test_categorical_default_true():
    """Test that fields are categorical by default."""
    extractor = MetadataExtractor()
    metadata = extractor.extract(CategoricalDataclass)

    # String, int, bool, uuid should be categorical
    assert metadata["name"].categorical is True
    assert metadata["age"].categorical is True
    assert metadata["status"].categorical is True
    assert metadata["category"].categorical is True
    assert metadata["count"].categorical is True
    assert metadata["uuid_field"].categorical is True


def test_categorical_false_for_float():
    """Test that float fields are non-categorical."""
    extractor = MetadataExtractor()
    metadata = extractor.extract(CategoricalDataclass)

    assert metadata["price"].categorical is False
    assert metadata["price"].field_type == float


def test_categorical_false_for_datetime():
    """Test that datetime fields are non-categorical."""
    extractor = MetadataExtractor()
    metadata = extractor.extract(CategoricalDataclass)

    assert metadata["timestamp"].categorical is False
    assert metadata["timestamp"].field_type == datetime


def test_categorical_false_for_timedelta():
    """Test that timedelta fields are non-categorical and numeric."""
    extractor = MetadataExtractor()
    metadata = extractor.extract(CategoricalDataclass)

    assert metadata["duration"].categorical is False
    assert metadata["duration"].numeric is True
    assert metadata["duration"].field_type == timedelta


def test_categorical_false_for_composite():
    """Test that composite fields are non-categorical."""
    extractor = MetadataExtractor()
    metadata = extractor.extract(PersonWithComposite)

    # Simple fields should be categorical
    assert metadata["name"].categorical is True
    assert metadata["age"].categorical is True

    # Composite field should be non-categorical
    assert metadata["address"].categorical is False
    assert metadata["address"].composite is True


def test_categorical_false_with_noncategorical_annotation():
    """Test that NonCategorical annotation marks fields as non-categorical."""
    extractor = MetadataExtractor()
    metadata = extractor.extract(CategoricalDataclass)

    # These are explicitly marked as non-categorical
    assert metadata["score"].categorical is False
    assert metadata["score"].field_type == int  # int is normally categorical

    assert metadata["rating"].categorical is False
    assert metadata["rating"].field_type == str  # str is normally categorical


def test_categorical_with_pydantic():
    """Test categorical detection works with Pydantic models."""
    extractor = MetadataExtractor()
    metadata = extractor.extract(CategoricalPydantic)

    # Categorical fields
    assert metadata["name"].categorical is True
    assert metadata["age"].categorical is True
    assert metadata["is_active"].categorical is True

    # Non-categorical fields
    assert metadata["price"].categorical is False
    assert metadata["created_at"].categorical is False
    assert metadata["duration"].categorical is False

    # Explicitly non-categorical
    assert metadata["score"].categorical is False


def test_categorical_with_optional_fields():
    """Test categorical detection with optional fields."""

    @dataclass
    class OptionalFields:
        name: str | None  # Categorical
        price: float | None  # Non-categorical
        score: Annotated[int, NonCategorical()] | None  # Explicitly non-categorical

    extractor = MetadataExtractor()
    metadata = extractor.extract(OptionalFields)

    assert metadata["name"].categorical is True
    assert metadata["name"].optional is True

    assert metadata["price"].categorical is False
    assert metadata["price"].optional is True

    assert metadata["score"].categorical is False
    assert metadata["score"].optional is True


def test_categorical_with_lists():
    """Test categorical detection with multivalued fields."""

    @dataclass
    class ListFields:
        tags: list[str]  # Categorical (items are categorical)
        prices: list[float]  # Non-categorical (items are non-categorical)
        scores: list[Annotated[int, NonCategorical()]]  # Explicitly non-categorical

    extractor = MetadataExtractor()
    metadata = extractor.extract(ListFields)

    # For list fields, categorical is based on the items_type
    assert metadata["tags"].categorical is True
    assert metadata["tags"].items_type == str

    assert metadata["prices"].categorical is False
    assert metadata["prices"].items_type == float

    # Note: NonCategorical on items doesn't affect the list itself
    # The list is categorical because the annotation is on items, not the list
    # This is consistent with how other annotations work (outer vs inner)
    assert metadata["scores"].categorical is True


def test_categorical_nested_fields():
    """Test categorical detection for nested composite fields."""

    @dataclass
    class Company:
        name: str
        revenue: float

    @dataclass
    class Employee:
        name: str
        company: Company

    extractor = MetadataExtractor()
    metadata = extractor.extract(Employee)

    # Simple field is categorical
    assert metadata["name"].categorical is True

    # Composite field is non-categorical
    assert metadata["company"].categorical is False

    # Nested simple field in composite is categorical
    assert metadata["company.name"].categorical is True

    # Nested float in composite is non-categorical
    assert metadata["company.revenue"].categorical is False

"""Tests for Literal type handling."""

from dataclasses import dataclass
from typing import Literal

from fields_metadata.extractor import MetadataExtractor


def test_literal_string_unwrapped_to_str():
    """Test that Literal['value'] is unwrapped to str."""

    @dataclass
    class Example:
        status: Literal["active", "inactive"]

    extractor = MetadataExtractor()
    metadata = extractor.extract(Example)

    assert metadata["status"].field_type == str
    assert metadata["status"].effective_type == str
    assert metadata["status"].original_annotation == Literal["active", "inactive"]


def test_literal_int_unwrapped_to_int():
    """Test that Literal[1, 2, 3] is unwrapped to int."""

    @dataclass
    class Example:
        priority: Literal[1, 2, 3]

    extractor = MetadataExtractor()
    metadata = extractor.extract(Example)

    assert metadata["priority"].field_type == int
    assert metadata["priority"].effective_type == int
    assert metadata["priority"].numeric is True


def test_literal_bool_unwrapped_to_bool():
    """Test that Literal[True, False] is unwrapped to bool."""

    @dataclass
    class Example:
        flag: Literal[True, False]

    extractor = MetadataExtractor()
    metadata = extractor.extract(Example)

    assert metadata["flag"].field_type == bool
    assert metadata["flag"].effective_type == bool


def test_optional_literal_unwrapped():
    """Test that Optional[Literal['value']] is unwrapped to str."""

    @dataclass
    class Example:
        status: Literal["pending", "done"] | None = None

    extractor = MetadataExtractor()
    metadata = extractor.extract(Example)

    assert metadata["status"].field_type == str
    assert metadata["status"].effective_type == str
    assert metadata["status"].optional is True


def test_literal_categorical_behavior():
    """Test that Literal fields have correct categorical behavior."""

    @dataclass
    class Example:
        status: Literal["active", "inactive"]
        priority: Literal[1, 2, 3]
        score: Literal[1.0, 2.0, 3.0]

    extractor = MetadataExtractor()
    metadata = extractor.extract(Example)

    # String literals should be categorical
    assert metadata["status"].categorical is True

    # Int literals should be categorical (int is categorical by default)
    assert metadata["priority"].categorical is True
    assert metadata["priority"].numeric is True

    # Float literals should be non-categorical (float is inherently non-categorical)
    assert metadata["score"].categorical is False
    assert metadata["score"].numeric is True

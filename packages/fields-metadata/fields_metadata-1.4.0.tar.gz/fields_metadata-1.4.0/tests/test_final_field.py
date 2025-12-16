"""Tests for the final field metadatum."""

from dataclasses import dataclass
from datetime import datetime

from fields_metadata.extractor import MetadataExtractor
from fields_metadata.metadata import FieldMetadata


@dataclass
class Address:
    """Nested composite type."""

    street: str
    city: str
    postal_code: str


@dataclass
class Money:
    """Composite type to be treated as final."""

    amount: float
    currency: str


@dataclass
class Person:
    """Test model with various field types."""

    name: str
    age: int
    created_at: datetime
    address: Address
    salary: Money


def test_primitive_fields_are_final() -> None:
    """Test that primitive fields are marked as final."""
    extractor = MetadataExtractor()
    metadata = extractor.extract(Person)

    # Primitive fields should be final
    assert metadata["name"].final is True
    assert metadata["name"].composite is False

    assert metadata["age"].final is True
    assert metadata["age"].composite is False

    assert metadata["created_at"].final is True
    assert metadata["created_at"].composite is False


def test_expanded_composite_fields_not_final() -> None:
    """Test that composite fields that are expanded are not final."""
    extractor = MetadataExtractor()
    metadata = extractor.extract(Person)

    # Address is composite and will be expanded, so not final
    assert metadata["address"].composite is True
    assert metadata["address"].final is False

    # Nested fields under address are final (primitives)
    assert metadata["address.street"].final is True
    assert metadata["address.city"].final is True
    assert metadata["address.postal_code"].final is True


def test_composite_in_final_types_is_final() -> None:
    """Test that composite fields marked as final_types are final."""
    extractor = MetadataExtractor(final_types={Money})
    metadata = extractor.extract(Person)

    # Money is in final_types, so it's treated as atomic (not composite)
    # and is final (has no subfields)
    assert metadata["salary"].composite is False  # Treated as atomic
    assert metadata["salary"].final is True

    # Money fields should not be expanded
    assert "salary.amount" not in metadata
    assert "salary.currency" not in metadata


def test_derived_fields_are_final() -> None:
    """Test that derived fields are final."""
    extractor = MetadataExtractor()

    # Register hook to create derived fields from datetime
    def datetime_hook(source: FieldMetadata) -> dict[str, FieldMetadata]:
        # Build the base path
        parts = [source.field_name]
        current = source.parent_field
        while current:
            parts.insert(0, current.field_name)
            current = current.parent_field
        base_path = ".".join(parts)

        return {
            f"{base_path}__year": FieldMetadata(
                field_name=f"{source.field_name}__year",
                field_type=int,
                effective_type=int,
                numeric=True,
                derived=True,
                final=True,  # Explicitly set, but should be default
            ),
        }

    extractor.register_type_hook(datetime, datetime_hook)

    metadata = extractor.extract(Person)

    # Original datetime field is final
    assert metadata["created_at"].final is True
    assert metadata["created_at"].derived is False

    # Derived field is also final
    assert metadata["created_at__year"].final is True
    assert metadata["created_at__year"].derived is True


def test_nested_composite_final_behavior() -> None:
    """Test final behavior with nested composite types."""

    @dataclass
    class Country:
        name: str
        code: str

    @dataclass
    class City:
        name: str
        country: Country

    @dataclass
    class Office:
        name: str
        city: City

    # Without final_types - all expanded
    extractor = MetadataExtractor()
    metadata = extractor.extract(Office)

    assert metadata["name"].final is True
    assert metadata["city"].final is False  # Has subfields
    assert metadata["city.name"].final is True
    assert metadata["city.country"].final is False  # Has subfields
    assert metadata["city.country.name"].final is True
    assert metadata["city.country.code"].final is True

    # With City as final - stops expansion at City
    extractor_with_final = MetadataExtractor(final_types={City})
    metadata_with_final = extractor_with_final.extract(Office)

    assert metadata_with_final["name"].final is True
    assert metadata_with_final["city"].composite is False  # Treated as atomic
    assert metadata_with_final["city"].final is True  # Marked as final
    assert "city.name" not in metadata_with_final  # Not expanded
    assert "city.country" not in metadata_with_final  # Not expanded


def test_multivalued_composite_final() -> None:
    """Test final behavior with multivalued composite fields."""

    @dataclass
    class Tag:
        name: str
        value: str

    @dataclass
    class Article:
        title: str
        tags: list[Tag]

    extractor = MetadataExtractor()
    metadata = extractor.extract(Article)

    # Article.tags is multivalued but the items are composite
    assert metadata["title"].final is True
    assert metadata["tags"].multivalued is True
    assert metadata["tags"].final is False  # Has subfields (tags.name, tags.value)

    # Nested fields through the list
    assert metadata["tags.name"].final is True
    assert metadata["tags.value"].final is True

    # With Tag as final
    extractor_with_final = MetadataExtractor(final_types={Tag})
    metadata_with_final = extractor_with_final.extract(Article)

    assert metadata_with_final["tags"].multivalued is True
    assert metadata_with_final["tags"].final is True  # Tag is final, so tags is final
    assert "tags.name" not in metadata_with_final
    assert "tags.value" not in metadata_with_final


def test_optional_composite_final() -> None:
    """Test final behavior with optional composite fields."""

    @dataclass
    class Contact:
        email: str
        phone: str

    @dataclass
    class User:
        username: str
        contact: Contact | None

    extractor = MetadataExtractor()
    metadata = extractor.extract(User)

    assert metadata["username"].final is True
    assert metadata["contact"].optional is True
    assert metadata["contact"].final is False  # Will be expanded
    assert metadata["contact.email"].final is True

    # With Contact as final
    extractor_with_final = MetadataExtractor(final_types={Contact})
    metadata_with_final = extractor_with_final.extract(User)

    assert metadata_with_final["contact"].optional is True
    assert metadata_with_final["contact"].final is True
    assert "contact.email" not in metadata_with_final


def test_all_fields_same_level_finality() -> None:
    """Test that fields at the same level have consistent final behavior."""

    @dataclass
    class Simple:
        text: str
        number: int
        flag: bool
        items: list[str]

    extractor = MetadataExtractor()
    metadata = extractor.extract(Simple)

    # All fields are final (no composite types)
    assert all(m.final for m in metadata.values())

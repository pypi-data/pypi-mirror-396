"""Tests for computed fields extraction."""

from dataclasses import dataclass

from pydantic import BaseModel, computed_field

from fields_metadata.extractor import MetadataExtractor


@dataclass
class DataclassWithTypedProperty:
    """Dataclass with typed property."""

    first_name: str
    last_name: str

    @property
    def full_name(self) -> str:
        """Computed full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def initials(self) -> str:
        """Computed initials."""
        return f"{self.first_name[0]}{self.last_name[0]}"


class PydanticWithComputedField(BaseModel):
    """Pydantic model with computed field."""

    first_name: str
    last_name: str

    @computed_field  # type: ignore[misc]
    @property
    def full_name(self) -> str:
        """Computed full name."""
        return f"{self.first_name} {self.last_name}"

    @computed_field  # type: ignore[misc]
    @property
    def name_length(self) -> int:
        """Computed name length."""
        return len(self.first_name) + len(self.last_name)


def test_dataclass_property_extracted():
    """Test that dataclass properties are extracted as computed fields."""
    extractor = MetadataExtractor()
    metadata = extractor.extract(DataclassWithTypedProperty)

    # Regular fields
    assert "first_name" in metadata
    assert "last_name" in metadata
    assert metadata["first_name"].computed is False
    assert metadata["last_name"].computed is False

    # Computed properties
    assert "full_name" in metadata
    assert metadata["full_name"].computed is True
    assert metadata["full_name"].field_type == str

    assert "initials" in metadata
    assert metadata["initials"].computed is True
    assert metadata["initials"].field_type == str


def test_pydantic_computed_field_extracted():
    """Test that Pydantic computed_field is extracted."""
    extractor = MetadataExtractor()
    metadata = extractor.extract(PydanticWithComputedField)

    # Regular fields
    assert "first_name" in metadata
    assert "last_name" in metadata
    assert metadata["first_name"].computed is False
    assert metadata["last_name"].computed is False

    # Computed fields
    assert "full_name" in metadata
    assert metadata["full_name"].computed is True
    assert metadata["full_name"].field_type == str

    assert "name_length" in metadata
    assert metadata["name_length"].computed is True
    assert metadata["name_length"].field_type == int


def test_computed_field_not_composite():
    """Test that computed fields are not considered composite."""

    @dataclass
    class Inner:
        value: str

    @dataclass
    class Outer:
        data: str

        @property
        def computed_inner(self) -> Inner:
            """Returns an Inner instance."""
            return Inner(value=self.data)

    extractor = MetadataExtractor()
    metadata = extractor.extract(Outer)

    assert "computed_inner" in metadata
    assert metadata["computed_inner"].computed is True
    assert metadata["computed_inner"].composite is True
    # Nested fields should be extracted
    assert "computed_inner.value" in metadata


def test_computed_field_with_list():
    """Test computed field returning a list."""

    @dataclass
    class WithListProperty:
        items: list[str]

        @property
        def item_count(self) -> int:
            """Number of items."""
            return len(self.items)

        @property
        def uppercase_items(self) -> list[str]:
            """Uppercase version of items."""
            return [item.upper() for item in self.items]

    extractor = MetadataExtractor()
    metadata = extractor.extract(WithListProperty)

    assert "item_count" in metadata
    assert metadata["item_count"].computed is True
    assert metadata["item_count"].field_type == int

    assert "uppercase_items" in metadata
    assert metadata["uppercase_items"].computed is True
    assert metadata["uppercase_items"].field_type == list
    assert metadata["uppercase_items"].items_type == str
    assert metadata["uppercase_items"].multivalued is True

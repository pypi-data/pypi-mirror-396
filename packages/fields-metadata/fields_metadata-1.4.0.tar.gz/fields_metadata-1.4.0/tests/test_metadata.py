"""Tests for FieldMetadata dataclass."""

from fields_metadata.metadata import FieldMetadata


def test_field_metadata_minimal_instantiation() -> None:
    """FieldMetadata can be instantiated with minimal required fields."""
    metadata = FieldMetadata(
        field_name="test_field",
        field_type=str,
    )
    assert metadata.field_name == "test_field"
    assert metadata.field_type == str


def test_field_metadata_default_values() -> None:
    """FieldMetadata has correct default values for optional fields."""
    metadata = FieldMetadata(
        field_name="test",
        field_type=str,
    )
    assert metadata.items_type is None
    assert metadata.effective_type is None
    assert metadata.multivalued is False
    assert metadata.composite is False
    assert metadata.parent_field is None
    assert metadata.numeric is False
    assert metadata.computed is False
    assert metadata.optional is False
    assert metadata.doc is None
    assert metadata.classification == {}
    assert metadata.extra == {}


def test_field_metadata_with_all_fields() -> None:
    """FieldMetadata can be instantiated with all fields specified."""
    metadata = FieldMetadata(
        field_name="child",
        field_type=list,
        items_type=str,
        effective_type=str,
        multivalued=True,
        composite=False,
        parent_field="parent",
        numeric=False,
        computed=False,
        optional=True,
        doc="Test documentation",
        classification={"semantic": "test_type"},
        extra={"min_length": 1, "max_length": 100},
    )

    assert metadata.field_name == "child"
    assert metadata.field_type == list
    assert metadata.items_type == str
    assert metadata.effective_type == str
    assert metadata.multivalued is True
    assert metadata.composite is False
    assert metadata.parent_field == "parent"
    assert metadata.numeric is False
    assert metadata.computed is False
    assert metadata.optional is True
    assert metadata.doc == "Test documentation"
    assert metadata.classification == {"semantic": "test_type"}
    assert metadata.extra == {"min_length": 1, "max_length": 100}


def test_field_metadata_classification_dict_is_mutable() -> None:
    """FieldMetadata classification dict can be modified after creation."""
    metadata = FieldMetadata(
        field_name="test",
        field_type=str,
    )
    metadata.classification["semantic"] = "person_name"
    assert metadata.classification["semantic"] == "person_name"


def test_field_metadata_extra_dict_is_mutable() -> None:
    """FieldMetadata extra dict can be modified after creation."""
    metadata = FieldMetadata(
        field_name="test",
        field_type=str,
    )
    metadata.extra["min_length"] = 5
    metadata.extra["max_length"] = 50
    assert metadata.extra["min_length"] == 5
    assert metadata.extra["max_length"] == 50


def test_field_metadata_numeric_field() -> None:
    """FieldMetadata can represent numeric fields."""
    metadata = FieldMetadata(
        field_name="age",
        field_type=int,
        numeric=True,
    )
    assert metadata.numeric is True


def test_field_metadata_computed_field() -> None:
    """FieldMetadata can represent computed fields."""
    metadata = FieldMetadata(
        field_name="full_name",
        field_type=str,
        computed=True,
    )
    assert metadata.computed is True


def test_field_metadata_composite_field() -> None:
    """FieldMetadata can represent composite fields."""
    metadata = FieldMetadata(
        field_name="address",
        field_type=object,
        composite=True,
    )
    assert metadata.composite is True


def test_field_metadata_multivalued_field() -> None:
    """FieldMetadata can represent multivalued fields."""
    metadata = FieldMetadata(
        field_name="tags",
        field_type=list,
        items_type=str,
        effective_type=str,
        multivalued=True,
    )
    assert metadata.multivalued is True
    assert metadata.items_type == str
    assert metadata.effective_type == str


def test_field_metadata_optional_field() -> None:
    """FieldMetadata can represent optional fields."""
    metadata = FieldMetadata(
        field_name="middle_name",
        field_type=str,
        optional=True,
    )
    assert metadata.optional is True


def test_field_metadata_nested_path() -> None:
    """FieldMetadata can represent fields at any nesting level."""
    metadata = FieldMetadata(
        field_name="postal_code",
        field_type=str,
    )
    # Field path is determined by the dictionary key, not stored in metadata
    assert metadata.field_name == "postal_code"


def test_field_metadata_parent_child_relationship() -> None:
    """FieldMetadata can maintain parent-child relationships."""
    child = FieldMetadata(
        field_name="street",
        field_type=str,
        parent_field="address",
    )

    assert child.parent_field == "address"

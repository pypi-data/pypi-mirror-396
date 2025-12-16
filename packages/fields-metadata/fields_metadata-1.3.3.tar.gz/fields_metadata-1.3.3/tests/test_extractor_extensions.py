"""Tests for extractor extension features: custom metadata class and lifecycle hooks."""

from dataclasses import dataclass, field
from typing import Any

import pytest

from fields_metadata import FieldMetadata, MetadataExtractor


@dataclass
class CustomFieldMetadata(FieldMetadata):
    """Custom metadata class with additional fields."""

    priority: str | None = None
    validation_rules: list[str] = field(default_factory=list)
    custom_flag: bool = False


@dataclass
class SimpleModel:
    """Simple model for testing."""

    name: str
    age: int


@dataclass
class NestedModel:
    """Nested model for testing."""

    title: str
    data: SimpleModel


class TestCustomMetadataClass:
    """Test custom metadata class functionality."""

    def test_default_metadata_class(self) -> None:
        """Test that default metadata class is FieldMetadata."""
        extractor = MetadataExtractor()
        metadata = extractor.extract(SimpleModel)

        assert isinstance(metadata["name"], FieldMetadata)
        assert type(metadata["name"]) is FieldMetadata

    def test_custom_metadata_class(self) -> None:
        """Test that custom metadata class is used."""
        extractor = MetadataExtractor[CustomFieldMetadata]()
        metadata = extractor.extract(SimpleModel)

        assert isinstance(metadata["name"], CustomFieldMetadata)
        assert isinstance(metadata["age"], CustomFieldMetadata)

        # Verify custom fields exist with default values
        assert metadata["name"].priority is None
        assert metadata["name"].validation_rules == []
        assert metadata["name"].custom_flag is False

    def test_custom_metadata_class_preserves_base_functionality(self) -> None:
        """Test that custom metadata class preserves base FieldMetadata functionality."""
        extractor = MetadataExtractor[CustomFieldMetadata]()
        metadata = extractor.extract(SimpleModel)

        # Check base functionality still works
        assert metadata["name"].field_name == "name"
        assert metadata["name"].field_type == str
        assert metadata["age"].field_type == int
        assert metadata["age"].numeric is True

    def test_custom_metadata_class_with_nested_structures(self) -> None:
        """Test that custom metadata class works with nested structures."""
        extractor = MetadataExtractor[CustomFieldMetadata]()
        metadata = extractor.extract(NestedModel)

        # All fields should use custom class
        assert isinstance(metadata["title"], CustomFieldMetadata)
        assert isinstance(metadata["data"], CustomFieldMetadata)
        assert isinstance(metadata["data.name"], CustomFieldMetadata)
        assert isinstance(metadata["data.age"], CustomFieldMetadata)

    def test_invalid_metadata_class_raises_error(self) -> None:
        """Test that non-FieldMetadata subclass raises TypeError."""

        class NotAMetadataClass:
            pass

        with pytest.raises(TypeError, match="must be a subclass of FieldMetadata"):
            MetadataExtractor[NotAMetadataClass]()  # type: ignore[type-var]

    def test_string_as_metadata_class_raises_error(self) -> None:
        """Test that passing a non-type raises TypeError."""
        with pytest.raises(TypeError, match="must be a subclass of FieldMetadata"):
            MetadataExtractor["not a class"]()  # type: ignore[type-var]

    def test_base_field_metadata_as_custom_class(self) -> None:
        """Test that FieldMetadata itself can be passed explicitly."""
        extractor = MetadataExtractor[FieldMetadata]()
        metadata = extractor.extract(SimpleModel)

        assert isinstance(metadata["name"], FieldMetadata)
        assert type(metadata["name"]) is FieldMetadata


class TestLifecycleHooks:
    """Test lifecycle hook functionality."""

    def test_before_extract_hook(self) -> None:
        """Test that before_extract hook is called."""
        called_with: list[type[Any]] = []

        def before_hook(obj_type: type[Any]) -> None:
            called_with.append(obj_type)

        extractor = MetadataExtractor()
        extractor.register_before_extract_hook(before_hook)
        extractor.extract(SimpleModel)

        assert len(called_with) == 1
        assert called_with[0] is SimpleModel

    def test_after_extract_hook(self) -> None:
        """Test that after_extract hook is called with correct data."""
        called_with: list[tuple[type[Any], dict[str, FieldMetadata]]] = []

        def after_hook(obj_type: type[Any], metadata: dict[str, FieldMetadata]) -> None:
            called_with.append((obj_type, metadata))

        extractor = MetadataExtractor()
        extractor.register_after_extract_hook(after_hook)
        result = extractor.extract(SimpleModel)

        assert len(called_with) == 1
        assert called_with[0][0] is SimpleModel
        assert called_with[0][1] is result
        assert "name" in called_with[0][1]
        assert "age" in called_with[0][1]

    def test_after_derived_hook(self) -> None:
        """Test that after_derived hook is called after derived fields are added."""
        from datetime import datetime

        @dataclass
        class ModelWithDatetime:
            created_at: datetime

        called_with: list[tuple[type[Any], dict[str, FieldMetadata]]] = []

        def after_derived_hook(obj_type: type[Any], metadata: dict[str, FieldMetadata]) -> None:
            called_with.append((obj_type, metadata))

        def datetime_hook(source: FieldMetadata) -> dict[str, FieldMetadata]:
            return {
                f"{source.field_name}__year": FieldMetadata(
                    field_name=f"{source.field_name}__year",
                    field_type=int,
                    effective_type=int,
                    derived=True,
                )
            }

        extractor = MetadataExtractor()
        extractor.register_type_hook(datetime, datetime_hook)
        extractor.register_after_derived_hook(after_derived_hook)
        result = extractor.extract(ModelWithDatetime)

        assert len(called_with) == 1
        assert called_with[0][0] is ModelWithDatetime
        # Should include both original and derived fields
        assert "created_at" in called_with[0][1]
        assert "created_at__year" in called_with[0][1]
        assert called_with[0][1] is result

    def test_after_extract_hook_can_modify_metadata(self) -> None:
        """Test that after_extract hook can modify metadata in place."""

        def modify_hook(obj_type: type[Any], metadata: dict[str, FieldMetadata]) -> None:
            for field_meta in metadata.values():
                field_meta.extra["modified"] = True

        extractor = MetadataExtractor()
        extractor.register_after_extract_hook(modify_hook)
        result = extractor.extract(SimpleModel)

        assert result["name"].extra["modified"] is True
        assert result["age"].extra["modified"] is True

    def test_after_derived_hook_can_modify_all_metadata(self) -> None:
        """Test that after_derived hook can modify both original and derived fields."""
        from datetime import datetime

        @dataclass
        class ModelWithDatetime:
            created_at: datetime

        def add_custom_property(obj_type: type[Any], metadata: dict[str, FieldMetadata]) -> None:
            for field_meta in metadata.values():
                field_meta.extra["processed"] = True

        def datetime_hook(source: FieldMetadata) -> dict[str, FieldMetadata]:
            return {
                f"{source.field_name}__year": FieldMetadata(
                    field_name=f"{source.field_name}__year",
                    field_type=int,
                    effective_type=int,
                    derived=True,
                )
            }

        extractor = MetadataExtractor()
        extractor.register_type_hook(datetime, datetime_hook)
        extractor.register_after_derived_hook(add_custom_property)
        result = extractor.extract(ModelWithDatetime)

        # Both original and derived fields should be modified
        assert result["created_at"].extra["processed"] is True
        assert result["created_at__year"].extra["processed"] is True

    def test_multiple_hooks_of_same_type(self) -> None:
        """Test that multiple hooks of the same type are all called."""
        call_order: list[str] = []

        def hook1(obj_type: type[Any]) -> None:
            call_order.append("hook1")

        def hook2(obj_type: type[Any]) -> None:
            call_order.append("hook2")

        def hook3(obj_type: type[Any]) -> None:
            call_order.append("hook3")

        extractor = MetadataExtractor()
        extractor.register_before_extract_hook(hook1)
        extractor.register_before_extract_hook(hook2)
        extractor.register_before_extract_hook(hook3)
        extractor.extract(SimpleModel)

        assert call_order == ["hook1", "hook2", "hook3"]

    def test_hook_execution_order(self) -> None:
        """Test that hooks are executed in the correct order."""
        execution_order: list[str] = []

        def before_hook(obj_type: type[Any]) -> None:
            execution_order.append("before")

        def after_hook(obj_type: type[Any], metadata: dict[str, FieldMetadata]) -> None:
            execution_order.append("after")

        def after_derived_hook(obj_type: type[Any], metadata: dict[str, FieldMetadata]) -> None:
            execution_order.append("after_derived")

        extractor = MetadataExtractor()
        extractor.register_before_extract_hook(before_hook)
        extractor.register_after_extract_hook(after_hook)
        extractor.register_after_derived_hook(after_derived_hook)
        extractor.extract(SimpleModel)

        assert execution_order == ["before", "after", "after_derived"]

    def test_hooks_not_called_with_cached_result(self) -> None:
        """Test that hooks are not called when returning cached results."""
        call_count = {"count": 0}

        def before_hook(obj_type: type[Any]) -> None:
            call_count["count"] += 1

        extractor = MetadataExtractor()
        extractor.register_before_extract_hook(before_hook)

        # First call should execute hook
        extractor.extract(SimpleModel)
        assert call_count["count"] == 1

        # Second call should use cache and not execute hook
        extractor.extract(SimpleModel)
        assert call_count["count"] == 1

    def test_hooks_called_with_refresh_cache(self) -> None:
        """Test that hooks are called again when refresh_cache=True."""
        call_count = {"count": 0}

        def before_hook(obj_type: type[Any]) -> None:
            call_count["count"] += 1

        extractor = MetadataExtractor()
        extractor.register_before_extract_hook(before_hook)

        # First call
        extractor.extract(SimpleModel)
        assert call_count["count"] == 1

        # Second call with refresh_cache should execute hook again
        extractor.extract(SimpleModel, refresh_cache=True)
        assert call_count["count"] == 2


class TestFieldLevelHooks:
    """Test field-level hook functionality."""

    def test_before_field_hook(self) -> None:
        """Test that before_field hook is called for each field."""
        calls: list[tuple[str, type[Any], type[Any]]] = []

        def before_field(field_name: str, field_type: type[Any], parent_type: type[Any]) -> None:
            calls.append((field_name, field_type, parent_type))

        extractor = MetadataExtractor()
        extractor.register_before_field_hook(before_field)
        extractor.extract(SimpleModel)

        assert len(calls) == 2
        assert calls[0] == ("name", str, SimpleModel)
        assert calls[1] == ("age", int, SimpleModel)

    def test_after_field_hook(self) -> None:
        """Test that after_field hook is called for each field."""
        calls: list[tuple[str, FieldMetadata, type[Any]]] = []

        def after_field(field_name: str, field_meta: FieldMetadata, parent_type: type[Any]) -> None:
            calls.append((field_name, field_meta, parent_type))

        extractor = MetadataExtractor()
        extractor.register_after_field_hook(after_field)
        result = extractor.extract(SimpleModel)

        assert len(calls) == 2
        assert calls[0][0] == "name"
        assert calls[0][1] is result["name"]
        assert calls[0][2] is SimpleModel
        assert calls[1][0] == "age"
        assert calls[1][1] is result["age"]

    def test_after_field_hook_can_modify_metadata(self) -> None:
        """Test that after_field hook can modify field metadata."""

        def enrich_field(
            field_name: str, field_meta: FieldMetadata, parent_type: type[Any]
        ) -> None:
            if field_meta.field_type == str:
                field_meta.extra["is_string"] = True
            if field_meta.numeric:
                field_meta.extra["is_numeric"] = True

        extractor = MetadataExtractor()
        extractor.register_after_field_hook(enrich_field)
        result = extractor.extract(SimpleModel)

        assert result["name"].extra["is_string"] is True
        assert "is_numeric" not in result["name"].extra
        assert result["age"].extra["is_numeric"] is True
        assert "is_string" not in result["age"].extra

    def test_field_hooks_with_custom_metadata(self) -> None:
        """Test field hooks with custom metadata class."""

        def set_priority(
            field_name: str, field_meta: FieldMetadata, parent_type: type[Any]
        ) -> None:
            if isinstance(field_meta, CustomFieldMetadata):
                if field_meta.field_type == str:
                    field_meta.priority = "high"
                else:
                    field_meta.priority = "low"

        extractor = MetadataExtractor[CustomFieldMetadata]()
        extractor.register_after_field_hook(set_priority)
        result = extractor.extract(SimpleModel)

        assert result["name"].priority == "high"
        assert result["age"].priority == "low"

    def test_field_hooks_with_nested_structures(self) -> None:
        """Test that field hooks are called for nested fields too."""
        all_fields: list[str] = []

        def track_field(field_name: str, field_meta: FieldMetadata, parent_type: type[Any]) -> None:
            all_fields.append(field_name)

        extractor = MetadataExtractor()
        extractor.register_after_field_hook(track_field)
        extractor.extract(NestedModel)

        assert "title" in all_fields
        assert "data" in all_fields
        assert "name" in all_fields
        assert "age" in all_fields

    def test_before_and_after_field_hooks_execution_order(self) -> None:
        """Test that before and after field hooks execute in correct order."""
        execution_order: list[str] = []

        def before_field(field_name: str, field_type: type[Any], parent_type: type[Any]) -> None:
            execution_order.append(f"before_{field_name}")

        def after_field(field_name: str, field_meta: FieldMetadata, parent_type: type[Any]) -> None:
            execution_order.append(f"after_{field_name}")

        extractor = MetadataExtractor()
        extractor.register_before_field_hook(before_field)
        extractor.register_after_field_hook(after_field)
        extractor.extract(SimpleModel)

        assert execution_order == [
            "before_name",
            "after_name",
            "before_age",
            "after_age",
        ]

    def test_multiple_field_hooks(self) -> None:
        """Test that multiple field hooks are all executed."""
        call_order: list[str] = []

        def hook1(field_name: str, field_meta: FieldMetadata, parent_type: type[Any]) -> None:
            call_order.append("hook1")

        def hook2(field_name: str, field_meta: FieldMetadata, parent_type: type[Any]) -> None:
            call_order.append("hook2")

        extractor = MetadataExtractor()
        extractor.register_after_field_hook(hook1)
        extractor.register_after_field_hook(hook2)
        extractor.extract(SimpleModel)

        assert call_order == ["hook1", "hook2", "hook1", "hook2"]

    def test_field_hooks_have_access_to_annotations(self) -> None:
        """Test that field hooks can access original annotations."""
        from typing import Annotated

        from annotated_types import DocInfo

        @dataclass
        class AnnotatedModel:
            name: Annotated[str, DocInfo("User name")]
            age: int

        annotations_found: list[Any] = []

        def check_annotations(
            field_name: str, field_meta: FieldMetadata, parent_type: type[Any]
        ) -> None:
            annotations_found.append(field_meta.original_annotation)
            if field_meta.doc:
                field_meta.extra["has_doc"] = True

        extractor = MetadataExtractor()
        extractor.register_after_field_hook(check_annotations)
        result = extractor.extract(AnnotatedModel)

        assert result["name"].extra.get("has_doc") is True
        assert "has_doc" not in result["age"].extra


class TestCombinedExtensions:
    """Test custom metadata class combined with lifecycle hooks."""

    def test_custom_metadata_with_after_extract_hook(self) -> None:
        """Test using custom metadata class with after_extract hook."""

        def enrich_metadata(obj_type: type[Any], metadata: dict[str, FieldMetadata]) -> None:
            for field_meta in metadata.values():
                if isinstance(field_meta, CustomFieldMetadata):
                    if field_meta.field_type == str:
                        field_meta.priority = "high"
                    else:
                        field_meta.priority = "low"

        extractor = MetadataExtractor[CustomFieldMetadata]()
        extractor.register_after_extract_hook(enrich_metadata)
        result = extractor.extract(SimpleModel)

        assert isinstance(result["name"], CustomFieldMetadata)
        assert result["name"].priority == "high"
        assert result["age"].priority == "low"

    def test_custom_metadata_with_multiple_hooks(self) -> None:
        """Test custom metadata class with multiple types of hooks."""

        def before_hook(obj_type: type[Any]) -> None:
            pass  # Just verify it's called

        def after_hook(obj_type: type[Any], metadata: dict[str, FieldMetadata]) -> None:
            for field_meta in metadata.values():
                if isinstance(field_meta, CustomFieldMetadata):
                    field_meta.validation_rules.append("required")

        def after_derived_hook(obj_type: type[Any], metadata: dict[str, FieldMetadata]) -> None:
            for field_meta in metadata.values():
                if isinstance(field_meta, CustomFieldMetadata):
                    field_meta.custom_flag = True

        extractor = MetadataExtractor[CustomFieldMetadata]()
        extractor.register_before_extract_hook(before_hook)
        extractor.register_after_extract_hook(after_hook)
        extractor.register_after_derived_hook(after_derived_hook)
        result = extractor.extract(SimpleModel)

        assert isinstance(result["name"], CustomFieldMetadata)
        assert "required" in result["name"].validation_rules
        assert result["name"].custom_flag is True
        assert result["age"].custom_flag is True

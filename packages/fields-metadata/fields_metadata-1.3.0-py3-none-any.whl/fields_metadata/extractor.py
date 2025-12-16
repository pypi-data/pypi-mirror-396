"""Main metadata extraction class."""

import dataclasses
import re
import typing
from collections.abc import Callable
from contextlib import suppress
from functools import singledispatchmethod
from typing import Any, Generic, TypeVar, cast, get_args, get_origin

from annotated_types import DocInfo, Ge, Le, Len, MaxLen, MinLen, Unit

from fields_metadata.annotations import (
    FinalType,
    HumanReadableId,
    InternationalURNAnnotation,
    Multiline,
    NonCategorical,
    SemanticClassification,
    is_marked_final_type,
)
from fields_metadata.metadata import FieldMetadata
from fields_metadata.type_utils import (
    extract_annotations_from_type,
    get_items_type,
    is_composite_type,
    is_computed_field,
    is_multivalued_type,
    is_non_categorical_type,
    is_numeric_type,
    is_optional_type,
    unwrap_annotated,
)

TMetadata = TypeVar("TMetadata", bound=FieldMetadata)


def _is_union_type(type_hint: type[Any]) -> bool:
    """Check if a type hint is a Union type (including Python 3.10+ | syntax)."""
    origin = get_origin(type_hint)
    if origin is typing.Union:
        return True
    try:
        from types import UnionType

        return origin is UnionType
    except ImportError:
        return False


class MetadataExtractor(Generic[TMetadata]):
    """
    Utility class to extract field metadata from composite objects.

    Supports custom metadata classes and lifecycle hooks for extensibility.

    Use as MetadataExtractor[CustomMetadata]() to specify a custom metadata type.
    """

    _metadata_class: type[TMetadata]

    def __init__(
        self,
        final_types: set[type[Any]] | None = None,
    ) -> None:
        """
        Initialize the metadata extractor.

        :param final_types: Set of types to treat as final (non-composite) even if
                           they are dataclasses or Pydantic models. These types will
                           not have their fields recursively extracted.
        """
        self.final_types = final_types or set()

        if not hasattr(self.__class__, "_metadata_class"):
            self.__class__._metadata_class = FieldMetadata  # type: ignore[assignment]

        self._type_hooks: dict[type[Any], list[Callable[[TMetadata], dict[str, TMetadata]]]] = {}
        self._name_hooks: list[
            tuple[Callable[[str], bool], Callable[[TMetadata], dict[str, TMetadata]]]
        ] = []
        self._cache: dict[type[Any], dict[str, TMetadata]] = {}

        self._before_extract_hooks: list[Callable[[type[Any]], None]] = []
        self._after_extract_hooks: list[Callable[[type[Any], dict[str, TMetadata]], None]] = []
        self._after_derived_hooks: list[Callable[[type[Any], dict[str, TMetadata]], None]] = []
        self._before_field_hooks: list[Callable[[str, type[Any], type[Any]], None]] = []
        self._after_field_hooks: list[Callable[[str, TMetadata, type[Any]], None]] = []

    def __class_getitem__(cls, item: type[TMetadata]) -> type["MetadataExtractor[TMetadata]"]:
        """
        Create a specialized extractor class for a specific metadata type.

        :param item: The FieldMetadata subclass to use
        :return: A specialized MetadataExtractor class
        """
        if not isinstance(item, type) or not issubclass(item, FieldMetadata):
            raise TypeError(
                f"MetadataExtractor type parameter must be a subclass of FieldMetadata, got {item}"
            )

        # Create a new class that inherits directly from MetadataExtractor
        class _SpecializedExtractor(cls):  # type: ignore[misc, valid-type]
            _metadata_class: type[TMetadata] = item

        return _SpecializedExtractor

    def register_type_hook(
        self,
        field_type: type[Any],
        callback: Callable[[TMetadata], dict[str, TMetadata]],
    ) -> None:
        """
        Register a hook to generate derived fields based on effective_type.

        :param field_type: The effective type that triggers this hook
        :param callback: Function that receives source metadata and returns
                        derived fields as dict[field_path, metadata]
        """
        if field_type not in self._type_hooks:
            self._type_hooks[field_type] = []
        self._type_hooks[field_type].append(callback)

    def register_name_hook(
        self,
        predicate: Callable[[str], bool] | str,
        callback: Callable[[TMetadata], dict[str, TMetadata]],
    ) -> None:
        """
        Register a hook to generate derived fields based on field name/path.

        :param predicate: Either a function that receives field_path and returns bool,
                         or a regex pattern string to match against field_path
        :param callback: Function that receives source metadata and returns
                        derived fields as dict[field_path, metadata]
        """
        if isinstance(predicate, str):
            pattern = re.compile(predicate)
            predicate_fn: Callable[[str], bool] = lambda path: bool(pattern.search(path))  # noqa: E731
        else:
            predicate_fn = predicate

        self._name_hooks.append((predicate_fn, callback))

    def register_before_extract_hook(
        self,
        callback: Callable[[type[Any]], None],
    ) -> None:
        """
        Register a hook to be called before extraction starts.

        The hook receives the type being extracted and can perform setup operations
        or validation before extraction begins.

        :param callback: Function that receives the type being extracted
        """
        self._before_extract_hooks.append(callback)

    def register_after_extract_hook(
        self,
        callback: Callable[[type[Any], dict[str, TMetadata]], None],
    ) -> None:
        """
        Register a hook to be called after field extraction but before derived field hooks.

        The hook receives the type and the extracted metadata dictionary. It can modify
        the metadata in place.

        :param callback: Function that receives the type and metadata dictionary
        """
        self._after_extract_hooks.append(callback)

    def register_after_derived_hook(
        self,
        callback: Callable[[type[Any], dict[str, TMetadata]], None],
    ) -> None:
        """
        Register a hook to be called after derived field hooks have been executed.

        The hook receives the type and the complete metadata dictionary (including
        derived fields). It can modify the metadata in place.

        :param callback: Function that receives the type and metadata dictionary
        """
        self._after_derived_hooks.append(callback)

    def register_before_field_hook(
        self,
        callback: Callable[[str, type[Any], type[Any]], None],
    ) -> None:
        """
        Register a hook to be called before extracting each field.

        The hook is called once per field before the field metadata is created.
        It receives the field name, field type, and parent type.

        :param callback: Function that receives field_name, field_type, and parent_type
        """
        self._before_field_hooks.append(callback)

    def register_after_field_hook(
        self,
        callback: Callable[[str, TMetadata, type[Any]], None],
    ) -> None:
        """
        Register a hook to be called after extracting each field.

        The hook is called once per field after the field metadata has been extracted
        and annotations have been processed. It receives the field name, the field
        metadata object, and the parent type. The hook can modify the metadata in place.

        This is ideal for populating custom metadata fields based on field properties.

        :param callback: Function that receives field_name, field_metadata, and parent_type
        """
        self._after_field_hooks.append(callback)

    def _is_final_type(self, effective_type: type[Any], field_type: type[Any]) -> bool:
        """
        Check if a type should be treated as final (non-composite).

        A type is considered final if any of these conditions are met:
        1. The type is in the self.final_types set (constructor parameter)
        2. The type has been decorated with @final_type
        3. The field type includes FinalType annotation

        :param effective_type: The effective type to check (unwrapped from containers)
        :param field_type: The original field type (may include Annotated wrapper)
        :return: True if the type should be treated as final
        """
        if effective_type in self.final_types:
            return True

        if is_marked_final_type(effective_type):
            return True

        return self._has_final_type_annotation(field_type)

    def _has_final_type_annotation(self, field_type: type[Any]) -> bool:
        """
        Check if a field type has the FinalType annotation.

        Handles:
        - Direct Annotated types: Annotated[Type, FinalType()]
        - Annotated wrapped in Union/Optional: Annotated[Type, FinalType()] | None
        - Annotated inside containers: list[Annotated[Type, FinalType()]]

        :param field_type: The field type to check
        :return: True if FinalType annotation is present
        """
        if get_origin(field_type) is typing.Annotated:
            annotations = extract_annotations_from_type(field_type)
            return any(isinstance(ann, FinalType) for ann in annotations)

        if _is_union_type(field_type):
            args = get_args(field_type)
            for arg in args:
                if arg is not type(None) and get_origin(arg) is typing.Annotated:
                    annotations = extract_annotations_from_type(arg)
                    if any(isinstance(ann, FinalType) for ann in annotations):
                        return True

        # Check inside multivalued containers (list, set, tuple, etc.)
        origin = get_origin(field_type)
        if origin in (list, set, tuple, frozenset):
            args = get_args(field_type)
            if args:
                # Check the first type argument for Annotated[..., FinalType()]
                first_arg = args[0]
                if get_origin(first_arg) is typing.Annotated:
                    annotations = extract_annotations_from_type(first_arg)
                    if any(isinstance(ann, FinalType) for ann in annotations):
                        return True

        return False

    def extract(self, obj_type: type[Any], refresh_cache: bool = False) -> dict[str, TMetadata]:
        """
        Extract metadata from all fields in a composite type.

        Results are cached per type. Subsequent calls with the same type will return
        cached results unless refresh_cache=True is specified.

        :param obj_type: The dataclass or pydantic model type to analyze
        :param refresh_cache: If True, ignore cached results and re-extract metadata
        :return: Dictionary mapping field paths to metadata objects
        :raises InvalidTypeUnionError: If field has union of non-None types
        :raises NoneTypeFieldError: If field has only None type
        """
        if not refresh_cache and obj_type in self._cache:
            return self._cache[obj_type]

        for hook in self._before_extract_hooks:
            hook(obj_type)

        result: dict[str, TMetadata] = {}

        fields = self._get_fields(obj_type)
        for field_name, field_type in fields:
            field_metadata = self._extract_field_metadata(
                field_name=field_name,
                field_type=field_type,
                parent_path="",
                obj_type=obj_type,
            )
            result.update(field_metadata)

        for hook in self._after_extract_hooks:  # type: ignore[assignment]
            hook(obj_type, result)  # type: ignore[call-arg]

        derived_fields = self._execute_all_hooks(result)
        result.update(derived_fields)

        for hook in self._after_derived_hooks:  # type: ignore[assignment]
            hook(obj_type, result)  # type: ignore[call-arg]

        self._update_human_readable_id_parents(result)

        self._cache[obj_type] = result

        return result

    def _execute_all_hooks(self, extracted_fields: dict[str, TMetadata]) -> dict[str, TMetadata]:
        """
        Execute all registered hooks on extracted fields to generate derived fields.

        :param extracted_fields: Dictionary of extracted field metadata
        :return: Dictionary of derived field metadata
        """
        derived_fields: dict[str, TMetadata] = {}

        for field_path, metadata in extracted_fields.items():
            if metadata.effective_type and metadata.effective_type in self._type_hooks:
                for hook in self._type_hooks[metadata.effective_type]:
                    hook_result = hook(metadata)
                    derived_fields.update(self._normalize_hook_result(hook_result, metadata))

            for predicate, hook in self._name_hooks:
                if predicate(field_path):
                    hook_result = hook(metadata)
                    derived_fields.update(self._normalize_hook_result(hook_result, metadata))

        return derived_fields

    def _normalize_hook_result(
        self,
        result: dict[str, TMetadata],
        _source_metadata: TMetadata,
    ) -> dict[str, TMetadata]:
        """
        Normalize hook result to ensure derived flag is set.

        :param result: Hook result as dictionary mapping field paths to metadata
        :param source_metadata: Source field metadata for error context
        :return: Normalized dictionary mapping paths to metadata
        """
        for metadata in result.values():
            if not metadata.derived:
                metadata.derived = True
        return result

    def _update_human_readable_id_parents(self, metadata: dict[str, TMetadata]) -> None:
        """
        Update parent fields with suggested_human_sorting_field for HumanReadableId children.

        When a field has the HumanReadableId annotation, its parent field (if any) will have
        extra['suggested_human_sorting_field'] set to the name of the human readable id field.

        :param metadata: Dictionary of field metadata to process
        """
        for _field_path, field_meta in metadata.items():
            if field_meta.extra.get("human_readable_id") is True and field_meta.parent_field:
                parent_field_path = field_meta.parent_field
                if parent_field_path in metadata:
                    parent_meta = metadata[parent_field_path]
                    parent_meta.extra["suggested_human_sorting_field"] = field_meta.field_name

    def _get_fields(self, obj_type: type[Any]) -> list[tuple[str, type[Any]]]:
        """
        Get fields from a dataclass or pydantic model, including computed fields.

        :param obj_type: The type to extract fields from
        :return: List of (field_name, field_type) tuples
        """
        result: list[tuple[str, type[Any]]] = []

        if dataclasses.is_dataclass(obj_type):
            fields = dataclasses.fields(obj_type)
            result.extend((f.name, cast(type[Any], f.type)) for f in fields)

            for name in dir(obj_type):
                if name.startswith("_"):
                    continue
                attr = getattr(obj_type, name, None)
                if isinstance(attr, property) and attr.fget is not None:
                    return_type = self._get_property_return_type(attr)
                    if return_type is not None:
                        result.append((name, return_type))

            return result

        with suppress(ImportError):
            from pydantic import BaseModel

            if isinstance(obj_type, type) and issubclass(obj_type, BaseModel):
                try:
                    type_hints = typing.get_type_hints(obj_type, include_extras=True)
                except Exception:
                    type_hints = getattr(obj_type, "__annotations__", {})

                model_fields = obj_type.model_fields
                for name in model_fields:
                    if name in type_hints:
                        result.append((name, cast(type[Any], type_hints[name])))

                computed_fields = getattr(obj_type, "__pydantic_computed_fields__", {})
                for name, computed_field_info in computed_fields.items():
                    field_type = computed_field_info.return_type
                    if field_type is not None:
                        result.append((name, cast(type[Any], field_type)))

                return result

        return result

    def _get_property_return_type(self, prop: property) -> type[Any] | None:
        """
        Extract return type from a property's type hints.

        :param prop: The property object
        :return: The return type, or None if not available
        """
        import inspect

        if prop.fget is None:
            return None

        try:
            hints = typing.get_type_hints(prop.fget)
            return hints.get("return")
        except Exception:
            with suppress(Exception):
                sig = inspect.signature(prop.fget)
                if sig.return_annotation != inspect.Signature.empty:
                    return sig.return_annotation  # type: ignore[no-any-return]

        return None

    def _extract_annotation_source(
        self, field_type: type[Any]
    ) -> tuple[type[Any] | None, type[Any]]:
        """
        Determine the source type for annotation extraction and prepare type for processing.

        This method detects if the field type contains Annotated wrappers and returns:
        1. The annotation source: original type if Annotated was found, None otherwise
        2. The type prepared for optional checking (with Annotated unwrapped from Union args)

        Examples:
            Annotated[str, Doc("x")] -> (Annotated[str, Doc("x")], str)
            str -> (None, str)
            Annotated[str, Doc("x")] | None -> (Annotated[str, Doc("x")] | None, str | None)

        :param field_type: The original field type
        :return: Tuple of (annotation_source, prepared_type)
        """
        if get_origin(field_type) is typing.Annotated:
            inner_type = get_args(field_type)[0]
            return field_type, inner_type

        if _is_union_type(field_type):
            args = get_args(field_type)
            for arg in args:
                if arg is not type(None) and get_origin(arg) is typing.Annotated:
                    inner_type = get_args(arg)[0]
                    new_args = tuple(inner_type if a == arg else a for a in args)
                    if len(new_args) == 2:
                        prepared_type = new_args[0] | new_args[1]
                    else:
                        from functools import reduce
                        from operator import or_

                        prepared_type = reduce(or_, new_args)
                    return field_type, prepared_type

        return None, field_type

    def _extract_field_metadata(
        self,
        field_name: str,
        field_type: type[Any],
        parent_path: str,
        obj_type: type[Any] | None = None,
    ) -> dict[str, TMetadata]:
        """
        Recursively extract metadata for a single field.

        :param field_name: Name of the field
        :param field_type: Type of the field
        :param parent_path: Dot-separated path to parent field
        :param obj_type: The containing object type (for computed field detection)
        :return: Dictionary with field path as key and metadata as value
        """
        if obj_type is not None:
            for hook in self._before_field_hooks:
                hook(field_name, field_type, obj_type)

        field_path = self._build_field_path(parent_path, field_name)

        annotation_source, prepared_type = self._extract_annotation_source(field_type)

        is_optional, non_none_type = is_optional_type(prepared_type)
        base_type = non_none_type if is_optional and non_none_type else prepared_type

        clean_type = unwrap_annotated(base_type)

        is_multivalued = is_multivalued_type(clean_type)
        items_type = get_items_type(clean_type) if is_multivalued else None
        effective_type = items_type if is_multivalued else clean_type

        field_type_for_metadata = clean_type
        if is_multivalued:
            origin = get_origin(clean_type)
            if origin is not None:
                field_type_for_metadata = cast(type[Any], origin)

        is_composite = (
            is_composite_type(effective_type)
            and not self._is_final_type(effective_type, field_type)
            if effective_type
            else False
        )
        is_numeric = is_numeric_type(effective_type) if effective_type else False
        is_computed = is_computed_field(obj_type, field_name) if obj_type is not None else False

        is_categorical = True
        if effective_type and is_non_categorical_type(effective_type):
            is_categorical = False
        if is_composite:
            is_categorical = False

        is_final = not (is_composite and effective_type is not None)

        metadata = self._metadata_class(
            field_name=field_name,
            field_type=field_type_for_metadata,
            items_type=items_type,
            effective_type=effective_type,
            multivalued=is_multivalued,
            composite=is_composite,
            parent_field=parent_path if parent_path else None,
            numeric=is_numeric,
            computed=is_computed,
            optional=is_optional,
            categorical=is_categorical,
            final=is_final,
            original_annotation=field_type,
        )

        if annotation_source is not None:
            self._process_annotations(annotation_source, metadata)

        if obj_type is not None:
            for hook in self._after_field_hooks:  # type: ignore[assignment]
                hook(field_name, metadata, obj_type)  # type: ignore[arg-type]

        result = {field_path: metadata}

        if is_composite and effective_type is not None:
            nested_fields = self._get_fields(effective_type)
            for nested_name, nested_type in nested_fields:
                nested_metadata = self._extract_field_metadata(
                    field_name=nested_name,
                    field_type=nested_type,
                    parent_path=field_path,
                    obj_type=effective_type,
                )
                result.update(nested_metadata)

        return result

    def _process_annotations(self, field_type: type[Any], metadata: TMetadata) -> None:
        """
        Process annotations from Annotated types and populate metadata.

        Handles both direct Annotated types and Annotated types wrapped in Union
        (e.g., Annotated[str, ...] | None).

        :param field_type: The field type (potentially Annotated or Union[Annotated, None])
        :param metadata: The metadata object to populate
        """
        if _is_union_type(field_type):
            args = get_args(field_type)
            for arg in args:
                if arg is not type(None) and get_origin(arg) is typing.Annotated:
                    self._process_annotations(arg, metadata)
                    return
            return

        if get_origin(field_type) is not typing.Annotated:
            return

        annotations = extract_annotations_from_type(field_type)

        for annotation in annotations:
            self._apply_annotation(annotation, metadata)

    @singledispatchmethod
    def _apply_annotation(self, annotation: Any, metadata: TMetadata) -> None:
        """
        Apply a single annotation to the metadata object.

        :param annotation: The annotation instance to process
        :param metadata: The metadata object to populate
        """

    @_apply_annotation.register
    def _(self, annotation: DocInfo, metadata: TMetadata) -> None:
        metadata.doc = annotation.documentation

    @_apply_annotation.register
    def _(self, annotation: Len, metadata: TMetadata) -> None:
        if annotation.min_length is not None:
            metadata.extra["min_length"] = annotation.min_length
        if annotation.max_length is not None:
            metadata.extra["max_length"] = annotation.max_length

    @_apply_annotation.register
    def _(self, annotation: MinLen, metadata: TMetadata) -> None:
        metadata.extra["min_length"] = annotation.min_length

    @_apply_annotation.register
    def _(self, annotation: MaxLen, metadata: TMetadata) -> None:
        metadata.extra["max_length"] = annotation.max_length

    @_apply_annotation.register
    def _(self, annotation: Ge, metadata: TMetadata) -> None:
        metadata.extra["min_value"] = annotation.ge

    @_apply_annotation.register
    def _(self, annotation: Le, metadata: TMetadata) -> None:
        metadata.extra["max_value"] = annotation.le

    @_apply_annotation.register
    def _(self, annotation: Unit, metadata: TMetadata) -> None:
        metadata.extra["unit"] = annotation.unit

    @_apply_annotation.register
    def _(self, annotation: SemanticClassification, metadata: TMetadata) -> None:
        metadata.classification["semantic"] = annotation.classification

    @_apply_annotation.register
    def _(self, _annotation: Multiline, metadata: TMetadata) -> None:
        metadata.extra["multiline"] = True

    @_apply_annotation.register
    def _(self, _annotation: HumanReadableId, metadata: TMetadata) -> None:
        metadata.extra["human_readable_id"] = True

    @_apply_annotation.register
    def _(self, _annotation: InternationalURNAnnotation, metadata: TMetadata) -> None:
        metadata.extra["urn_type"] = "international"

    @_apply_annotation.register
    def _(self, _annotation: NonCategorical, metadata: TMetadata) -> None:
        metadata.categorical = False

    def _build_field_path(self, parent_path: str, field_name: str) -> str:
        """
        Build dot-separated field path.

        :param parent_path: Parent field path
        :param field_name: Current field name
        :return: Complete field path
        """
        if parent_path:
            return f"{parent_path}.{field_name}"
        return field_name


__all__ = [
    "MetadataExtractor",
]

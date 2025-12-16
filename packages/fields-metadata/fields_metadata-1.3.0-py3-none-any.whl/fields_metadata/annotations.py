"""Custom annotation types for field metadata."""

from dataclasses import dataclass
from typing import Any, TypeVar

_T = TypeVar("_T")


@dataclass(frozen=True)
class Multiline:
    """Annotation to mark a string field as multiline text."""


@dataclass(frozen=True)
class HumanReadableId:
    """Annotation to mark a field as a human-readable identifier."""


@dataclass(frozen=True)
class SemanticClassification:
    """
    Annotation for semantic classification of a field.

    :param classification: The semantic classification value
    """

    classification: str


@dataclass(frozen=True)
class URNAnnotation:
    """Annotation to mark a field as a URN."""


@dataclass(frozen=True)
class InternationalURNAnnotation(URNAnnotation):
    """Annotation to mark a field as an international URN."""


@dataclass(frozen=True)
class NonCategorical:
    """Annotation to mark a field as non-categorical."""


@dataclass(frozen=True)
class FinalType:
    """
    Annotation to mark a type as final (non-composite).

    When used with typing.Annotated, prevents the metadata extractor from
    traversing into the type's fields.

    Example:
        from typing import Annotated
        from fields_metadata.annotations import FinalType

        # Mark a field's type as final
        value: Annotated[MyCustomType, FinalType()]
    """


_FINAL_TYPE_MARKER = "__fields_metadata_final_type__"


def final_type(cls: type[_T]) -> type[_T]:
    """
    Decorator to mark a class as a final type.

    Final types are not traversed by the metadata extractor, even if they
    are dataclasses or Pydantic models.

    :param cls: The class to mark as final
    :return: The same class with final type marker

    Example:
        from fields_metadata.annotations import final_type

        @final_type
        @dataclass
        class MyCustomType:
            value: str
    """
    setattr(cls, _FINAL_TYPE_MARKER, True)
    return cls


def is_marked_final_type(cls: Any) -> bool:
    """
    Check if a class has been marked as a final type using the decorator.

    :param cls: The class to check
    :return: True if the class is marked as final, False otherwise
    """
    return getattr(cls, _FINAL_TYPE_MARKER, False) is True


__all__ = [
    "Multiline",
    "HumanReadableId",
    "SemanticClassification",
    "URNAnnotation",
    "InternationalURNAnnotation",
    "NonCategorical",
    "FinalType",
    "final_type",
    "is_marked_final_type",
]

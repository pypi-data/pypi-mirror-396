"""Sample dataclass models for testing."""

from dataclasses import dataclass
from typing import Annotated

from annotated_types import DocInfo, Ge, Le, MaxLen, MinLen

from fields_metadata.annotations import HumanReadableId, Multiline, SemanticClassification


@dataclass
class SimpleDataclass:
    """Simple dataclass with basic fields."""

    name: str
    age: int
    active: bool


@dataclass
class DataclassWithOptional:
    """Dataclass with optional fields."""

    name: str
    email: str | None = None
    phone: str | None = None


@dataclass
class DataclassWithAnnotations:
    """Dataclass with various annotations."""

    name: Annotated[str, HumanReadableId(), DocInfo("Person's full name")]
    age: Annotated[int, Ge(0), Le(150)]
    bio: Annotated[str | None, Multiline()] = None
    tags: Annotated[list[str], MinLen(1), MaxLen(10)] | None = None


@dataclass
class DataclassWithSemantic:
    """Dataclass with semantic classification."""

    person_name: Annotated[str, SemanticClassification("person_name")]
    email: Annotated[str, SemanticClassification("email")]


@dataclass
class Address:
    """Address dataclass for nesting."""

    street: str
    city: str
    postal_code: str


@dataclass
class NestedDataclass:
    """Dataclass with nested composite fields."""

    name: str
    address: Address


@dataclass
class DeepNestedDataclass:
    """Dataclass with deep nesting."""

    name: str
    address: Address | None = None


@dataclass
class DataclassWithList:
    """Dataclass with list fields."""

    tags: list[str]
    scores: list[int]
    addresses: list[Address]


@dataclass
class DataclassWithProperty:
    """Dataclass with computed property."""

    first_name: str
    last_name: str

    @property
    def full_name(self) -> str:
        """Computed full name."""
        return f"{self.first_name} {self.last_name}"


@dataclass
class DataclassWithNumericTypes:
    """Dataclass with various numeric types."""

    age: int
    height: float
    is_active: bool


@dataclass
class InvalidUnionDataclass:
    """Dataclass with invalid union (multiple non-None types)."""

    field: str | int


@dataclass
class NoneOnlyDataclass:
    """Dataclass with None-only field."""

    field: None


@dataclass
class Author:
    """Author with human-readable ID."""

    name: Annotated[str, HumanReadableId()]
    email: str


@dataclass
class Article:
    """Article with nested author."""

    title: str
    author: Author


@dataclass
class Location:
    """Location with human-readable building ID."""

    building_id: Annotated[str, HumanReadableId()]
    floor: int


@dataclass
class Department:
    """Department with nested location."""

    name: str
    location: Location


@dataclass
class Company:
    """Company with nested department."""

    company_name: str
    department: Department

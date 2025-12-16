# fields-metadata

A Python library for extracting comprehensive field metadata from dataclasses and Pydantic models, with support for derived fields, custom annotations, and recursive traversal of nested structures.

## Overview

`fields-metadata` provides a powerful `MetadataExtractor` utility that analyzes composite objects (dataclasses and Pydantic models) and returns detailed metadata about their fields, including:

- **Field types and paths**: Dot-separated paths for nested fields
- **Type detection**: Optional, multivalued, composite, numeric, and categorical field detection
- **Computed fields**: Support for properties and Pydantic computed fields
- **Custom annotations**: Extensible annotation system with built-in annotations
- **Hook system**: Hook-based extensibility mechanism, allowing synthetic fields, custom extraction, and more
- **Recursive traversal**: Automatic extraction of nested structure metadata
- **Original annotations**: Preserves original type annotations including `Annotated` and `Union` types
- **Type-safe generics**: Generic support for custom metadata types with full type inference

## Installation

```bash
pip install fields-metadata
```

## Quick Start

```python
from dataclasses import dataclass
from typing import Annotated
from annotated_types import DocInfo, Ge
from fields_metadata import MetadataExtractor, HumanReadableId

@dataclass
class Address:
    street: str
    city: str
    postal_code: str

@dataclass
class Person:
    name: Annotated[str, HumanReadableId(), DocInfo("Person's full name")]
    age: Annotated[int, Ge(0), DocInfo("Person's age in years")]
    email: str | None = None
    address: Address | None = None

# Create extractor with default FieldMetadata
extractor = MetadataExtractor()
metadata = extractor.extract(Person)

# Access field metadata
print(metadata["name"].doc)  # "Person's full name"
print(metadata["name"].extra["human_readable_id"])  # True
print(metadata["age"].numeric)  # True
print(metadata["age"].extra["min_value"])  # 0
print(metadata["email"].optional)  # True

# Access nested field metadata
if "address.street" in metadata:
    street_meta = metadata["address.street"]
    print(street_meta.field_name)  # "street"
    print(street_meta.parent_field)  # "address"
```

## Core Features

### Caching

Metadata extraction results are automatically cached per type to improve performance:

```python
extractor = MetadataExtractor()

# First extraction - processes the entire type
metadata1 = extractor.extract(Person)

# Second extraction - returns cached result instantly
metadata2 = extractor.extract(Person)
assert metadata1 is metadata2  # Same dictionary object

# Force refresh if type definition changed
metadata3 = extractor.extract(Person, refresh_cache=True)
```

**Note**: Caching is done per `MetadataExtractor` instance. If you modify a type definition at runtime, use `refresh_cache=True` to re-extract metadata.

### Field Paths

Field paths uniquely identify fields in the metadata hierarchy:

- **Dictionary Keys**: Field paths are used as keys in the returned `dict[str, FieldMetadata]`
- **Nested Fields**: Use dot notation (`.`) for composite fields: `"address.street"`, `"company.departments.name"`
- **Derived Fields**: Use double underscore (`__`) for derived fields: `"created_at__year"`, `"price__normalized"`
- **No `field_path` Attribute**: The `FieldMetadata` class does not store the field path - it's implicit in the dictionary key

```python
@dataclass
class Address:
    street: str
    city: str

@dataclass
class Person:
    name: str
    address: Address

extractor = MetadataExtractor()
metadata = extractor.extract(Person)

# Field paths are the dictionary keys
assert "name" in metadata
assert "address" in metadata
assert "address.street" in metadata
assert "address.city" in metadata

# To get the full path of a field, traverse parent relationships
def get_field_path(field_meta: FieldMetadata) -> str:
    parts = [field_meta.field_name]
    current = field_meta.parent_field
    while current:
        parts.insert(0, current.field_name)
        current = current.parent_field
    return ".".join(parts)

street_path = get_field_path(metadata["address.street"])
assert street_path == "address.street"
```

### Field Metadata Properties

Each `FieldMetadata` object contains comprehensive information:

#### Basic Properties

- **field_name**: The name of the field
- **field_type**: The type of the field (simplified for multivalued types)
- **effective_type**: The actual type being used (items_type for collections, field_type otherwise)
- **original_annotation**: The original field type annotation (preserves `Annotated`, `Union`, etc.)

#### Type Flags

- **multivalued**: `True` for lists, tuples, sets, frozensets
- **composite**: `True` for nested dataclasses/Pydantic models
- **optional**: `True` for `Optional` types or `Union` with `None`
- **numeric**: `True` for int, float, Decimal, datetime, date, time, timedelta (excluding bool)
- **categorical**: `True` for categorical fields (False for numeric types, composite, or NonCategorical)
- **computed**: `True` for properties and Pydantic computed fields
- **derived**: `True` for synthetic fields generated through hooks from other fields
- **final**: `True` for fields with no non-derived subfields (primitives or composite types marked as final)

#### Metadata

- **items_type**: For collections, the type of items; `None` otherwise
- **parent_field**: Field path (string) of the parent field for nested fields (e.g., `"address"` for `"address.street"`); `None` for root fields
- **doc**: Documentation from `DocInfo` annotation
- **classification**: Dictionary with classification metadata
- **extra**: Dictionary for additional metadata (constraints, flags, etc.)

### Supported Field Types

#### Dataclasses

```python
from dataclasses import dataclass

@dataclass
class Product:
    name: str
    price: float
    tags: list[str]

    @property
    def display_price(self) -> str:
        return f"${self.price:.2f}"

extractor = MetadataExtractor()
metadata = extractor.extract(Product)

# Regular fields
assert metadata["name"].field_type == str
assert metadata["price"].numeric is True

# Multivalued fields
assert metadata["tags"].multivalued is True
assert metadata["tags"].items_type == str

# Computed fields (properties)
assert metadata["display_price"].computed is True
```

#### Pydantic Models

```python
from pydantic import BaseModel, computed_field

class User(BaseModel):
    username: str
    email: str
    age: int

    @computed_field
    @property
    def email_domain(self) -> str:
        return self.email.split("@")[1]

extractor = MetadataExtractor()
metadata = extractor.extract(User)

assert metadata["email_domain"].computed is True
```

#### Literal Types

Literal types are automatically unwrapped to their underlying type:

```python
from dataclasses import dataclass
from typing import Literal

@dataclass
class Task:
    name: str
    status: Literal["pending", "in_progress", "done"]
    priority: Literal[1, 2, 3]
    score: Literal[1.0, 2.0, 3.0]

extractor = MetadataExtractor()
metadata = extractor.extract(Task)

# Literal types are unwrapped to their underlying type
assert metadata["status"].field_type == str
assert metadata["status"].effective_type == str
assert metadata["status"].categorical is True

assert metadata["priority"].field_type == int
assert metadata["priority"].numeric is True
assert metadata["priority"].categorical is True  # int is categorical by default

assert metadata["score"].field_type == float
assert metadata["score"].numeric is True
assert metadata["score"].categorical is False  # float is non-categorical
```

### Nested Structures

The library automatically traverses nested structures and builds dot-separated paths:

```python
from dataclasses import dataclass

@dataclass
class Department:
    name: str
    budget: float

@dataclass
class Company:
    name: str
    departments: list[Department]

extractor = MetadataExtractor()
metadata = extractor.extract(Company)

# Root fields
assert "name" in metadata
assert "departments" in metadata

# Nested fields (through list)
assert "departments.name" in metadata
assert "departments.budget" in metadata

# Check relationships
dept_name = metadata["departments.name"]
assert dept_name.parent_field == metadata["departments"]
```

### Categorical vs Non-Categorical Fields

Fields are automatically classified as categorical or non-categorical:

```python
from dataclasses import dataclass
from datetime import datetime
from fields_metadata.annotations import NonCategorical

@dataclass
class Record:
    status: str              # Categorical
    count: int               # Categorical
    score: float             # Non-categorical (continuous)
    timestamp: datetime      # Non-categorical (temporal)
    category: Annotated[str, NonCategorical()]  # Explicitly non-categorical

extractor = MetadataExtractor()
metadata = extractor.extract(Record)

assert metadata["status"].categorical is True
assert metadata["count"].categorical is True
assert metadata["score"].categorical is False  # Float is non-categorical
assert metadata["timestamp"].categorical is False  # Datetime is non-categorical
assert metadata["category"].categorical is False  # Explicit annotation
```

### Custom Annotations

#### Built-in Annotations

```python
from typing import Annotated
from annotated_types import DocInfo, Len, MinLen, MaxLen, Ge, Le, Unit
from fields_metadata import (
    FinalType,
    Multiline,
    HumanReadableId,
    SemanticClassification,
    InternationalURNAnnotation,
    NonCategorical,
    final_type,
)

@dataclass
class Article:
    title: Annotated[str, MinLen(1), MaxLen(200), DocInfo("Article title")]
    content: Annotated[str, Multiline(), DocInfo("Article body")]
    word_count: Annotated[int, Ge(0), Le(10000), Unit("words")]
    category: Annotated[str, SemanticClassification("topic")]
    article_id: Annotated[str, HumanReadableId()]
    urn: Annotated[str, InternationalURNAnnotation()]

extractor = MetadataExtractor()
metadata = extractor.extract(Article)

# DocInfo annotation
assert metadata["title"].doc == "Article title"

# Length constraints
assert metadata["title"].extra["min_length"] == 1
assert metadata["title"].extra["max_length"] == 200

# Value constraints
assert metadata["word_count"].extra["min_value"] == 0
assert metadata["word_count"].extra["max_value"] == 10000
assert metadata["word_count"].extra["unit"] == "words"

# Custom annotations
assert metadata["content"].extra["multiline"] is True
assert metadata["article_id"].extra["human_readable_id"] is True
assert metadata["urn"].extra["urn_type"] == "international"
assert metadata["category"].classification["semantic"] == "topic"
```

#### Supported `annotated-types` Annotations

- **DocInfo**: Field documentation → `metadata.doc`
- **Len, MinLen, MaxLen**: Length constraints → `metadata.extra['min_length']`, `metadata.extra['max_length']`
- **Ge, Le**: Value constraints → `metadata.extra['min_value']`, `metadata.extra['max_value']`
- **Unit**: Unit information → `metadata.extra['unit']`

#### Custom Library Annotations

- **FinalType**: Marks a field's type as final (prevents traversal) → `metadata.composite = False`
  - Use with `Annotated` for per-field control: `Annotated[Money, FinalType()]`
  - Works with containers and optional types
  - See [Final Types](#final-types) section for detailed usage
- **final_type**: Decorator to mark a class as a final type
  - Apply to dataclasses or Pydantic models: `@final_type @dataclass class Money: ...`
  - See [Final Types](#final-types) section for detailed usage
- **Multiline**: Marks multiline text fields → `metadata.extra['multiline']`
- **HumanReadableId**: Marks human-readable identifiers → `metadata.extra['human_readable_id']`
  - Sets `extra['human_readable_id'] = True` on the annotated field
  - If the field has a parent, sets `extra['suggested_human_sorting_field']` on the parent to the field name
- **SemanticClassification**: Semantic field classification → `metadata.classification['semantic']`
- **InternationalURNAnnotation**: Marks international URN fields → `metadata.extra['urn_type']`
- **NonCategorical**: Explicitly marks field as non-categorical → `metadata.categorical = False`

#### HumanReadableId Parent Field Behavior

When a nested field has the `HumanReadableId` annotation, it affects both the field itself and its parent:

```python
from dataclasses import dataclass
from typing import Annotated
from fields_metadata import MetadataExtractor, HumanReadableId

@dataclass
class Author:
    name: Annotated[str, HumanReadableId()]
    email: str

@dataclass
class Article:
    title: str
    author: Author

extractor = MetadataExtractor()
metadata = extractor.extract(Article)

# The author.name field has human_readable_id set to True
assert metadata["author.name"].extra["human_readable_id"] is True

# The parent field (author) has suggested_human_sorting_field set to the full path
# This can be used as a direct lookup key in the metadata dictionary
assert metadata["author"].extra["suggested_human_sorting_field"] == "author.name"
```

This pattern helps identify which nested field should be used for human-readable sorting or display purposes when dealing with composite types. The full path is provided so it can be used directly as a lookup key in the metadata dictionary.

### Final Types

Control recursive expansion of composite types by marking them as "final". The library provides three complementary approaches that can be used together:

#### Approach 1: Constructor Parameter (Original)

Pass a set of types to the `MetadataExtractor` constructor:

```python
from dataclasses import dataclass

@dataclass
class Money:
    amount: float
    currency: str

@dataclass
class Product:
    name: str
    price: Money

# Specify final types via constructor
extractor = MetadataExtractor(final_types={Money})
metadata = extractor.extract(Product)

assert "price" in metadata
assert "price.amount" not in metadata  # Not expanded
assert metadata["price"].composite is False  # Treated as atomic
assert metadata["price"].final is True
```

#### Approach 2: Class Decorator (New in 1.3.0)

Use the `@final_type` decorator to mark your own classes:

```python
from fields_metadata import final_type

@final_type  # Mark as final type
@dataclass
class Money:
    amount: float
    currency: str

@dataclass
class Product:
    name: str
    price: Money

# No need to pass final_types parameter!
extractor = MetadataExtractor()
metadata = extractor.extract(Product)

assert "price" in metadata
assert "price.amount" not in metadata  # Not expanded
assert metadata["price"].composite is False
```

**Benefits:**

- More explicit and self-documenting
- No need to maintain a separate list of final types
- Works automatically with any extractor instance

#### Approach 3: Field Annotation (New in 1.3.0)

Use the `FinalType` annotation for fine-grained control per field:

```python
from typing import Annotated
from fields_metadata import FinalType

@dataclass
class Money:
    amount: float
    currency: str

@dataclass
class Product:
    name: str
    regular_price: Money  # This Money field will be expanded
    special_price: Annotated[Money, FinalType()]  # This one won't

extractor = MetadataExtractor()
metadata = extractor.extract(Product)

# regular_price is expanded
assert "regular_price.amount" in metadata
assert "regular_price.currency" in metadata

# special_price is NOT expanded due to FinalType annotation
assert "special_price" in metadata
assert "special_price.amount" not in metadata
assert metadata["special_price"].composite is False
```

**Benefits:**

- Per-field control over expansion
- Works with types you cannot modify (third-party classes)
- Ideal for selectively treating the same type differently in different contexts

**Works with containers and optional types:**

```python
@dataclass
class Document:
    # FinalType annotation in list
    tags: list[Annotated[Tag, FinalType()]]

    # FinalType annotation with optional
    author: Annotated[Author, FinalType()] | None

extractor = MetadataExtractor()
metadata = extractor.extract(Document)

# Tag and Author fields are not expanded
assert "tags" in metadata
assert "tags.name" not in metadata  # Tag fields not expanded
assert metadata["tags"].composite is False

assert "author" in metadata
assert "author.name" not in metadata  # Author fields not expanded
```

#### Combining All Three Approaches

All three methods work together and can be mixed as needed:

```python
from fields_metadata import final_type, FinalType

@dataclass
class TypeA:
    value: str

@final_type
@dataclass
class TypeB:
    value: str

@dataclass
class TypeC:
    value: str

@dataclass
class Container:
    a: TypeA  # Will be expanded (no final marking)
    b: TypeB  # Won't be expanded (@final_type decorator)
    c: Annotated[TypeC, FinalType()]  # Won't be expanded (FinalType annotation)

# Pass TypeA via constructor for consistency
extractor = MetadataExtractor(final_types={TypeA})
metadata = extractor.extract(Container)

# TypeA not expanded (constructor parameter)
assert "a" in metadata
assert "a.value" not in metadata

# TypeB not expanded (decorator)
assert "b" in metadata
assert "b.value" not in metadata

# TypeC not expanded (annotation)
assert "c" in metadata
assert "c.value" not in metadata
```

#### Understanding `final`

The `final` property indicates whether a field has no non-derived subfields:

```python
@dataclass
class Product:
    name: str
    price: Money

# Without final marking
extractor = MetadataExtractor()
metadata = extractor.extract(Product)

assert metadata["name"].final is True  # Primitive, no subfields
assert metadata["price"].final is False  # Has subfields (amount, currency)
assert metadata["price.amount"].final is True  # Primitive leaf

# With final marking
extractor = MetadataExtractor(final_types={Money})
metadata = extractor.extract(Product)

assert metadata["name"].final is True  # Still primitive
assert metadata["price"].final is True  # Now treated as atomic (no subfields)
```

**Key points:**

- A field is `final=True` when it has no non-derived subfields
- This happens for:
  - Primitive types (str, int, float, datetime, etc.)
  - Composite types marked as final (not expanded)
  - Derived fields (always final, even if their source field is also final)
- Useful for determining which fields are "leaf" fields in the metadata tree

### Multivalued Annotations

Annotations can be applied to collections or their items:

```python
from typing import Annotated

@dataclass
class Dataset:
    # Annotation on the list itself
    outer: Annotated[list[int], DocInfo("Outer doc")]

    # Annotation on the items
    inner: list[Annotated[int, DocInfo("Inner doc")]]

    # Both (outer takes precedence)
    both: Annotated[list[Annotated[int, DocInfo("Inner")]], DocInfo("Outer")]

extractor = MetadataExtractor()
metadata = extractor.extract(Dataset)

assert metadata["outer"].doc == "Outer doc"
assert metadata["inner"].doc == "Inner doc"
assert metadata["both"].doc == "Outer"  # Outer annotation wins
```

### Optional and Union Types

```python
@dataclass
class Config:
    # Optional field
    timeout: int | None

    # Also works with typing.Optional
    from typing import Optional
    retries: Optional[int]

extractor = MetadataExtractor()
metadata = extractor.extract(Config)

assert metadata["timeout"].optional is True
assert metadata["timeout"].field_type == int  # None is stripped

assert metadata["retries"].optional is True
assert metadata["retries"].field_type == int

# Invalid: Union of multiple non-None types
# from fields_metadata.exceptions import InvalidTypeUnionError
# @dataclass
# class Invalid:
#     value: int | str  # Raises InvalidTypeUnionError
```

### Accessing Parent-Child Relationships

```python
from fields_metadata import FieldsPath

@dataclass
class Address:
    street: str
    city: str

@dataclass
class Person:
    name: str
    address: Address

extractor = MetadataExtractor()
metadata = extractor.extract(Person)

street = metadata["address.street"]
assert street.parent_field == "address"
assert metadata["address"].parent_field is None

path = FieldsPath.from_field_metadata("address.street", metadata)
assert path.get_path_string() == "address.street"

for field_meta in path:
    print(f"{field_meta.field_name}: {field_meta.field_type}")
```

## Extensibility

The library provides a comprehensive extensibility system through custom metadata classes, derived field hooks, and lifecycle hooks.

### Custom Metadata Classes with Generics

You can create custom `FieldMetadata` subclasses to add application-specific fields and use generics for full type safety:

```python
from dataclasses import dataclass, field
from fields_metadata import MetadataExtractor, FieldMetadata

@dataclass
class CustomFieldMetadata(FieldMetadata):
    """Custom metadata with extra fields."""
    priority: str | None = None
    validation_rules: list[str] = field(default_factory=list)
    custom_flag: bool = False

# Use generic syntax for type-safe extraction
extractor = MetadataExtractor[CustomFieldMetadata]()
metadata = extractor.extract(MyModel)

# All metadata objects are properly typed as CustomFieldMetadata
assert isinstance(metadata["field_name"], CustomFieldMetadata)

# IDE autocomplete and type checking work for custom fields
metadata["field_name"].priority = "high"
metadata["field_name"].validation_rules.append("required")
metadata["field_name"].custom_flag = True
```

**Benefits of the generic approach:**

- **Type safety**: Full type inference and checking by mypy
- **IDE support**: Autocomplete for custom metadata fields
- **No runtime parameters**: Cleaner API with type information at class definition
- **Works everywhere**: Custom metadata type applies to all fields (manual, computed, simple, composite, derived, multivalued)

**Legacy syntax** (still supported):

```python
# Pre-v1.2.0 syntax - still works but less type-safe
extractor = MetadataExtractor(metadata_class=CustomFieldMetadata)
```

The custom class must be a subclass of `FieldMetadata`. All extracted metadata will use your custom class, including nested and derived fields.

### Derived Field Hooks

The hook system allows automatic generation of derived field metadata based on field types or names.

#### Type-Based Hooks

Generate derived fields based on the field's `effective_type`:

**API**: `register_type_hook(field_type, callback)`

- **field_type** (`type[Any]`): The type that triggers this hook (e.g., `datetime`, `int`)
- **callback** (`Callable[[TMetadata], dict[str, TMetadata]]`): Function that receives the source field's metadata and returns a dictionary mapping derived field paths to their metadata objects

```python
from datetime import datetime
from dataclasses import dataclass
from fields_metadata import MetadataExtractor, FieldMetadata, FieldsPath

@dataclass
class Event:
    title: str
    event_datetime: datetime

extractor = MetadataExtractor()

def datetime_components(source: FieldMetadata) -> dict[str, FieldMetadata]:
    """Extract year, month, day of week from datetime fields."""
    metadata_map = extractor._cache.get(Event, {})
    field_path_obj = FieldsPath.from_field_metadata(source.field_name, metadata_map)

    if field_path_obj:
        base_path = field_path_obj.get_path_string(complimentary=True)
    else:
        base_path = source.field_name

    return {
        f"{base_path}__year": FieldMetadata(
            field_name=f"{source.field_name}__year",
            field_type=int,
            effective_type=int,
            numeric=True,
            derived=True,
            parent_field=base_path,
            doc='Year of the date',
            extra={
                'suggested_validation': 'year',
            },
        ),
        f"{base_path}__month": FieldMetadata(
            field_name=f"{source.field_name}__month",
            field_type=int,
            effective_type=int,
            numeric=True,
            derived=True,
            parent_field=base_path,
            doc='Month of the date',
            extra={
                'min_value': 1,
                'max_value': 12,
                'suggested_validation': 'month',
            },
        ),
        f"{base_path}__dow": FieldMetadata(
            field_name=f"{source.field_name}__dow",
            field_type=int,
            effective_type=int,
            numeric=True,
            derived=True,
            parent_field=base_path,
            doc='Day of the week for the date',
            extra={
                'min_value': 1,
                'max_value': 7,
                'suggested_validation': 'dow',
            },
        ),
    }

extractor.register_type_hook(datetime, datetime_components)

metadata = extractor.extract(Event)

assert metadata["event_datetime"].field_type == datetime
assert metadata["event_datetime__year"].derived is True
assert metadata["event_datetime__month"].derived is True
assert metadata["event_datetime__dow"].derived is True
```

#### Name-Based Hooks

Generate derived fields based on field name patterns:

**API**: `register_name_hook(predicate, callback)`

- **predicate** (`Callable[[str], bool] | str`): Either a function that takes the field path and returns `bool`, or a regex pattern string to match against the field path
- **callback** (`Callable[[TMetadata], dict[str, TMetadata]]`): Function that receives the source field's metadata and returns a dictionary mapping derived field paths to their metadata objects

```python
from fields_metadata import MetadataExtractor, FieldMetadata, FieldsPath

@dataclass
class Report:
    title: str
    reported_by_organization_id: str

extractor = MetadataExtractor()

def normalize_org_id(source: FieldMetadata) -> dict[str, FieldMetadata]:
    """Generate normalized organization ID field."""
    metadata_map = extractor._cache.get(Report, {})
    field_path_obj = FieldsPath.from_field_metadata(source.field_name, metadata_map)

    if field_path_obj:
        base_path = field_path_obj.get_path_string(complimentary=True)
    else:
        base_path = source.field_name

    return {
        f"{base_path}__normalized": FieldMetadata(
            field_name=f"{source.field_name}__normalized",
            field_type=str,
            effective_type=str,
            derived=True,
            parent_field=source.parent_field,
            doc=f"Normalized version of {source.field_name}",
        ),
    }

# Using regex pattern
extractor.register_name_hook(r".*organization.*id$", normalize_org_id)

# Using predicate function
extractor.register_name_hook(
    lambda path: path.endswith("_id"),
    normalize_org_id
)

metadata = extractor.extract(Report)
assert "reported_by_organization_id__normalized" in metadata
```

**Note**: Derived fields use double underscore (`__`) as separator to distinguish them from original fields.

### Lifecycle Hooks

Register callbacks to execute at different stages of the extraction process.

#### Before Extract Hook

Called before extraction begins. Receives the type being extracted for setup or validation.

```python
def before_extract(obj_type: type[Any]) -> None:
    print(f"Starting extraction for {obj_type.__name__}")

extractor = MetadataExtractor()
extractor.register_before_extract_hook(before_extract)
```

**Parameters:**

- `obj_type`: The dataclass or Pydantic model type being extracted

#### After Extract Hook

Called after field extraction completes, before derived field hooks execute. Receives the extracted metadata dictionary for modification.

```python
def after_extract(obj_type: type[Any], metadata: dict[str, FieldMetadata]) -> None:
    for field_meta in metadata.values():
        if field_meta.field_type == str:
            field_meta.extra["string_field"] = True

extractor = MetadataExtractor()
extractor.register_after_extract_hook(after_extract)
```

**Parameters:**

- `obj_type`: The type being extracted
- `metadata`: Dictionary mapping field paths to their metadata objects

#### After Derived Hook

Called after all derived field hooks have executed. Receives the complete metadata dictionary including derived fields.

```python
def after_derived(obj_type: type[Any], metadata: dict[str, FieldMetadata]) -> None:
    for field_meta in metadata.values():
        field_meta.extra["processed"] = True

extractor = MetadataExtractor()
extractor.register_after_derived_hook(after_derived)
```

**Parameters:**

- `obj_type`: The type being extracted
- `metadata`: Complete dictionary including original and derived fields

#### Field-Level Hooks

Called for each individual field during extraction, including nested fields.

```python
def before_field(field_name: str, field_type: type[Any], parent_type: type[Any]) -> None:
    print(f"Extracting field {field_name} of type {field_type}")

def after_field(field_name: str, field_meta: FieldMetadata, parent_type: type[Any]) -> None:
    if field_meta.field_type == str:
        field_meta.extra["string_field"] = True

extractor = MetadataExtractor()
extractor.register_before_field_hook(before_field)
extractor.register_after_field_hook(after_field)
```

**Before Field Parameters:**

- `field_name`: Name of the field being extracted
- `field_type`: Original type annotation of the field
- `parent_type`: The containing class/model type

**After Field Parameters:**

- `field_name`: Name of the extracted field
- `field_meta`: Complete field metadata object with all properties and annotations
- `parent_type`: The containing class/model type

The after-field hook is ideal for populating custom metadata fields based on individual field properties.

### Combining Extensions

Combine custom metadata classes with lifecycle hooks and derived field hooks for powerful customization:

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

@dataclass
class AppMetadata(FieldMetadata):
    """Application-specific metadata."""
    priority: str = "normal"
    validated: bool = False
    tags: list[str] = field(default_factory=list)

def set_priority(field_name: str, field_meta: FieldMetadata, parent_type: type[Any]) -> None:
    """Set priority based on field type."""
    if isinstance(field_meta, AppMetadata):
        if field_meta.field_type == str:
            field_meta.priority = "high"
        elif field_meta.numeric:
            field_meta.priority = "medium"

def mark_validated(obj_type: type[Any], metadata: dict[str, FieldMetadata]) -> None:
    """Mark all fields as validated after extraction."""
    for field_meta in metadata.values():
        if isinstance(field_meta, AppMetadata):
            field_meta.validated = True

def datetime_hook(source: AppMetadata) -> dict[str, AppMetadata]:
    """Create derived year field for datetime fields."""
    return {
        f"{source.field_name}__year": AppMetadata(
            field_name=f"{source.field_name}__year",
            field_type=int,
            effective_type=int,
            derived=True,
            priority="auto",
            tags=["temporal", "derived"],
        )
    }

# Create extractor with custom metadata using generics
extractor = MetadataExtractor[AppMetadata]()

# Register all hooks
extractor.register_after_field_hook(set_priority)
extractor.register_after_derived_hook(mark_validated)
extractor.register_type_hook(datetime, datetime_hook)

# Extract with full customization
metadata = extractor.extract(MyModel)

# All fields have custom metadata with proper typing
assert all(isinstance(m, AppMetadata) for m in metadata.values())
```

**Important notes:**

- Lifecycle hooks are only called during actual extraction, not when returning cached results
- Use `refresh_cache=True` to force re-execution of hooks
- When using custom metadata classes with generics, hook callbacks receive and return the custom type
- All extensibility features work together seamlessly for maximum flexibility

## Development

```bash
# Install dependencies
uv sync --dev

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov

# Run linting
uv run ruff check fields_metadata tests

# Run type checking
uv run mypy fields_metadata

# Run all checks with tox
tox
```

## License

MIT License

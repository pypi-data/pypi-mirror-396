"""fields-metadata: A Python library for extracting field metadata from dataclasses and Pydantic models."""

from fields_metadata.annotations import (
    FinalType,
    HumanReadableId,
    InternationalURNAnnotation,
    Multiline,
    NonCategorical,
    SemanticClassification,
    URNAnnotation,
    final_type,
)
from fields_metadata.exceptions import (
    FieldMetadataError,
    InvalidTypeUnionError,
    NoneTypeFieldError,
)
from fields_metadata.extractor import MetadataExtractor
from fields_metadata.metadata import FieldMetadata
from fields_metadata.path import FieldsMetadataMap, FieldsPath

__version__ = "1.3.3"

__all__ = [
    "MetadataExtractor",
    "FieldMetadata",
    "FieldsPath",
    "FieldsMetadataMap",
    "FinalType",
    "Multiline",
    "HumanReadableId",
    "NonCategorical",
    "SemanticClassification",
    "URNAnnotation",
    "InternationalURNAnnotation",
    "final_type",
    "FieldMetadataError",
    "InvalidTypeUnionError",
    "NoneTypeFieldError",
    "__version__",
]

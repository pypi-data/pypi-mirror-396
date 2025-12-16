"""Custom exceptions for fields-metadata library."""


class FieldMetadataError(Exception):
    """Base exception for fields-metadata library."""


class InvalidTypeUnionError(FieldMetadataError):
    """Raised when a field has a union between non-None types."""


class NoneTypeFieldError(FieldMetadataError):
    """Raised when a field has only None as its type."""


__all__ = [
    "FieldMetadataError",
    "InvalidTypeUnionError",
    "NoneTypeFieldError",
]

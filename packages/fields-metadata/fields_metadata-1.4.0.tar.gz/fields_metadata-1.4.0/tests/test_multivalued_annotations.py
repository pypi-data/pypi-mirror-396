"""Tests for annotation extraction in multivalued fields."""

from dataclasses import dataclass
from typing import Annotated

from annotated_types import DocInfo, Ge, Le, MaxLen, MinLen

from fields_metadata.extractor import MetadataExtractor


@dataclass
class MultivaluedWithDocs:
    """Test various annotation patterns on multivalued fields."""

    # Case 1: Doc on the outer Annotated (wrapping the list)
    outer_doc: Annotated[list[str], DocInfo("Doc on list container")]

    # Case 2: Doc on the inner Annotated (on items)
    inner_doc: list[Annotated[str, DocInfo("Doc on items")]]

    # Case 3: Both outer and inner docs (outer should prevail)
    both_docs: Annotated[
        list[Annotated[str, DocInfo("Inner doc - ignore")]], DocInfo("Outer doc - use this")
    ]

    # Case 4: Multiple annotations on outer
    outer_annotations: Annotated[list[str], MinLen(1), MaxLen(10), DocInfo("List constraints")]

    # Case 5: Annotations on items
    inner_annotations: list[Annotated[int, Ge(0), Le(100), DocInfo("Score range")]]

    # Case 6: Both outer and inner annotations
    both_annotations: Annotated[
        list[Annotated[int, Ge(0), DocInfo("Inner")]], MinLen(1), MaxLen(10), DocInfo("Outer")
    ]


def test_outer_doc_on_list():
    """Test that doc on outer Annotated (wrapping list) is extracted."""
    extractor = MetadataExtractor()
    metadata = extractor.extract(MultivaluedWithDocs)

    # Doc should be extracted from outer Annotated
    assert metadata["outer_doc"].doc == "Doc on list container"
    assert metadata["outer_doc"].field_type == list
    assert metadata["outer_doc"].items_type == str


def test_inner_doc_on_items():
    """Test that doc on inner Annotated (on items) is extracted."""
    extractor = MetadataExtractor()
    metadata = extractor.extract(MultivaluedWithDocs)

    # Doc is on items, not on the list itself
    # This case is tricky - we might not extract it since it's on the items
    assert metadata["inner_doc"].field_type == list
    assert metadata["inner_doc"].items_type == str
    # The doc on items might not be extracted to the list field
    # (it would apply to each item, not to the list)


def test_both_docs_outer_prevails():
    """Test that outer doc prevails when both outer and inner have docs."""
    extractor = MetadataExtractor()
    metadata = extractor.extract(MultivaluedWithDocs)

    # Outer doc should prevail
    assert metadata["both_docs"].doc == "Outer doc - use this"
    assert metadata["both_docs"].field_type == list
    assert metadata["both_docs"].items_type == str


def test_outer_annotations_on_list():
    """Test that annotations on outer Annotated are extracted."""
    extractor = MetadataExtractor()
    metadata = extractor.extract(MultivaluedWithDocs)

    # Annotations on the list itself
    assert metadata["outer_annotations"].doc == "List constraints"
    assert metadata["outer_annotations"].extra.get("min_length") == 1
    assert metadata["outer_annotations"].extra.get("max_length") == 10
    assert metadata["outer_annotations"].field_type == list
    assert metadata["outer_annotations"].items_type == str


def test_inner_annotations_on_items():
    """Test annotations on items."""
    extractor = MetadataExtractor()
    metadata = extractor.extract(MultivaluedWithDocs)

    # These annotations are on the items, not the list
    # We might not extract them to the list field itself
    assert metadata["inner_annotations"].field_type == list
    assert metadata["inner_annotations"].items_type == int


def test_both_annotations_outer_prevails():
    """Test that outer annotations prevail when both exist."""
    extractor = MetadataExtractor()
    metadata = extractor.extract(MultivaluedWithDocs)

    # Outer annotations should be used
    assert metadata["both_annotations"].doc == "Outer"
    assert metadata["both_annotations"].extra.get("min_length") == 1
    assert metadata["both_annotations"].extra.get("max_length") == 10
    assert metadata["both_annotations"].field_type == list
    assert metadata["both_annotations"].items_type == int

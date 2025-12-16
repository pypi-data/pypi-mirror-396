"""Field path navigation utilities."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

from fields_metadata.metadata import FieldMetadata

FieldsMetadataMap = dict[str, FieldMetadata]


@dataclass
class FieldsPath:
    """
    Class encapsulating dually both a path of fields as well as a single step of the path,
    in the form of a double-linked list.

    This class is intended to ease the traversal of field paths descending and ascending in the
    hierarchy of fields.
    """

    name: str
    metadata: FieldMetadata
    prev: FieldsPath | None = None
    next: FieldsPath | None = None

    def __iter__(self) -> Iterator[FieldsPath]:
        current: FieldsPath | None = self
        while current:
            yield current
            current = current.next

    @property
    def last(self) -> FieldsPath:
        """Get the last node in the path."""
        current: FieldsPath = self
        while current.next:
            current = current.next
        return current

    def get_path_string(
        self,
        composite_separator: str = ".",
        derivate_separator: str = "__",
        complimentary: bool = False,
    ) -> str:
        """
        Generate a string that represents the sequence of steps in the path.

        :param composite_separator: String used to "glue" the next step in the string when it is a composite field, defaults to '.'
        :type composite_separator: str, optional
        :param derivate_separator: String used to "glue" the next step in the string when it is a derivate field, defaults to '__'
        :type derivate_separator: str, optional
        :param complimentary: Whether to generate the string downwards from this point (``False``) or until this point (``True``),
            defaults to ``False``.
        :type complimentary: bool, optional
        :return: The string representing the sequence of steps.
        :rtype: str
        """
        current: FieldsPath = self
        output_string: str = current.name
        if complimentary:
            while current.prev:
                if current.prev.metadata.composite:
                    output_string = f"{current.prev.name}{composite_separator}{output_string}"
                elif current.metadata.derived:
                    output_string = f"{current.prev.name}{derivate_separator}{output_string}"
                current = current.prev
        else:
            while current.next:
                if current.metadata.composite:
                    output_string += f"{composite_separator}{current.next.name}"
                elif current.next.metadata.derived:
                    output_string += f"{derivate_separator}{current.next.name}"
                current = current.next
        return output_string

    @staticmethod
    def from_field_metadata(
        full_field_name: str, fields_metadata: FieldsMetadataMap
    ) -> FieldsPath | None:
        """
        Constructor method that creates a field path from its full name and a dictionary of fields
        metadata containing the metadata of the field and all of its ancestors.

        :param full_field_name: The full field path (e.g., 'address.street' or 'date__year')
        :type full_field_name: str
        :param fields_metadata: Dictionary mapping field paths to their metadata
        :type fields_metadata: FieldsMetadataMap
        :return: The field path, or ``None`` if it could not be built.
        :rtype: Optional[FieldsPath]
        """
        current_full_field_name: str | None = full_field_name
        current_field_name: str
        current_field_metadata: FieldMetadata
        current_node: FieldsPath | None = None
        descendant_node: FieldsPath | None = None

        while current_full_field_name:
            if current_node:
                descendant_node = current_node
                current_node = None

            if current_full_field_name not in fields_metadata:
                return None

            current_field_metadata = fields_metadata[current_full_field_name]

            if current_field_metadata.derived:
                if "__" in current_full_field_name:
                    current_full_field_name, current_field_name = current_full_field_name.rsplit(
                        "__", maxsplit=1
                    )
                else:
                    current_field_name = current_full_field_name
                    current_full_field_name = None
            elif current_field_metadata.parent_field:
                if "." in current_full_field_name:
                    current_full_field_name, current_field_name = current_full_field_name.rsplit(
                        ".", maxsplit=1
                    )
                else:
                    current_field_name = current_full_field_name
                    current_full_field_name = None
            else:
                current_field_name = current_full_field_name
                current_full_field_name = None

            current_node = FieldsPath(name=current_field_name, metadata=current_field_metadata)
            if descendant_node:
                current_node.next = descendant_node
                descendant_node.prev = current_node

        if not current_node:
            return None
        return current_node

    @staticmethod
    def full_doc(fields_path: FieldsPath) -> list[str]:
        """
        Generate the full documentation string for the given fields path,
        concatenating the documentation of each step in the path.

        :param fields_path: The fields path to generate the documentation for.
        :type fields_path: FieldsPath
        :return: The full documentation strings sequence.
        :rtype: list[str]
        """
        docs: list[str] = []
        for step in fields_path:
            if step.metadata.doc:
                docs.append(step.metadata.doc)
        return docs


__all__ = [
    "FieldsPath",
    "FieldsMetadataMap",
]

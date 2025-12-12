from __future__ import annotations

from abc import ABCMeta
from functools import cached_property

from .._objects import CorbelProperty


class CorbelMeta(ABCMeta):
    """
    Metaclass to automatically register Corbel properties for dataclasses.

    Tracks properties, cached_properties, and CorbelProperty instances
    across the class and its bases. Excludes a predefined set of internal
    attributes to avoid conflicts.
    """

    __corbel_properties = frozenset[str](
        [
            "_corbel_initialized",
            "_corbel_validation",
            "_corbel_asdict",
            "_corbel_dirty_fields",
            "corbel_fields",
            "corbel_field_names",
            "corbel_properties",
            "corbel_property_names",
        ]
    )

    def __new__(cls, name: str, bases: tuple[type, ...], cls_dict: dict[str, object]):
        """
        Create a new class, automatically collecting Corbel properties.

        :param name:
            Name of the new class being created.
        :param bases:
            Tuple of base classes the new class inherits from.
        :param cls_dict:
            Dictionary of class attributes and methods.
        :return:
            Newly created class with `__corbel_properties__` registered.
        """
        properties: dict[str, object] = {}
        for base in bases:
            if hasattr(base, "__corbel_properties__"):
                properties.update(base.__corbel_properties__)

        for attr_name, attr_value in cls_dict.items():
            if attr_name in cls.__corbel_properties:
                continue

            if isinstance(attr_value, (property, cached_property, CorbelProperty)):
                properties[attr_name] = attr_value

        cls_dict["__corbel_properties__"] = properties
        return super().__new__(cls, name, bases, cls_dict)


__all__ = ("CorbelMeta",)

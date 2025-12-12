from __future__ import annotations

from dataclasses import Field
from functools import cached_property
from typing import Any, TYPE_CHECKING

from ._base import BaseMixin
from .._objects import CorbelProperty
from .._utils import corbel_metadata

if TYPE_CHECKING:
    from ..types import Member


class MembersMixin(BaseMixin):
    __corbel_metadata_cache = dict[type, dict[tuple[Any, str | None], Any]]()

    @classmethod
    def corbel_metadata(
        cls,
        member: Any,
        path: str | None = None,
        default: Any = None,
    ) -> Any:
        """
        Retrieve Corbel-specific metadata for a member, using caching.

        :param member:
            The field or property whose metadata to retrieve.
        :param path:
            Optional path within nested metadata.
        :param default:
            Default value to return if metadata is not found.
        :return:
            The cached or computed metadata value.
        """
        cache = cls.__corbel_metadata_cache.setdefault(cls, {})
        key = (member, path)

        if key not in cache:
            cache[key] = corbel_metadata(member, path, default)

        return cache[key]

    @cached_property
    def corbel_fields(
        self,
    ) -> tuple[Field, ...]:
        """
        Return a tuple of dataclass fields for this instance.

        Cached for repeated introspection to avoid recomputation.

        :return:
            Tuple of dataclasses.Field objects.
        """
        fields: dict[str, Field] = getattr(self, "__dataclass_fields__", {})
        return tuple(f for f in fields.values() if isinstance(f, Field))

    @cached_property
    def corbel_field_names(
        self,
    ) -> set[str]:
        """
        Return the set of dataclass field names for this instance.

        Cached for repeated access. Useful for validation and updates.

        :return:
            Set of field name strings.
        """
        return {f.name for f in self.corbel_fields}

    @cached_property
    def corbel_properties(
        self,
    ) -> tuple[property | CorbelProperty, ...]:
        """
        Return a tuple of property objects for this instance.

        Cached for repeated introspection. Excludes private and dunder attributes.

        :return:
            Tuple of property or CorbelProperty objects.
        """
        properties: dict[str, Field] = getattr(self, "__corbel_properties__", {})
        return tuple(p for p in properties.values() if isinstance(p, property))

    @property
    def corbel_property_names(
        self,
    ) -> set[str]:
        """
        Return the set of property names for this instance.

        Cached for efficiency.

        :return:
            Set of property name strings.
        """
        properties: dict[str, property] = getattr(self, "__corbel_properties__", {})
        return {p for p in properties.keys()}

    def corbel_members(
        self,
        include_properties: bool = True,
        include_private: bool = False,
    ) -> dict[str, Member]:
        """
        Return a mapping of member names to Field or property objects.

        Includes fields by default and optionally properties. Can filter private
        members.

        :param include_properties:
            Include properties if True.
        :param include_private:
            Include private members if True.
        :return:
            Dictionary of member names to Field or property objects.
        """
        members: dict[str, Any] = {
            k: v
            for k, v in getattr(self, "__dataclass_fields__", {}).items()
            if include_private or not k.startswith("_")
        }

        if include_properties:
            properties: dict[str, Any] = {
                k: v
                for k, v in getattr(self, "__corbel_properties__", {}).items()
                if include_private or not k.startswith("_")
            }

            members |= properties

        return members

    def corbel_member_names(
        self,
        include_properties: bool = True,
        include_private: bool = False,
    ) -> set[str]:
        """
        Return a set of member names (fields and optionally properties).

        Can exclude private members.

        :param include_properties:
            Include properties if True.
        :param include_private:
            Include private members if True.
        :return:
            Set of member names.
        """
        member_names: set[str] = self.corbel_field_names.copy()

        if include_properties:
            member_names |= self.corbel_property_names.copy()

        if not include_private:
            return set(filter(lambda n: not n.startswith("_"), member_names))

        return member_names


__all__ = ("MembersMixin",)

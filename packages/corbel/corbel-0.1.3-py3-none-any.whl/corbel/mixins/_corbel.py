from __future__ import annotations

from dataclasses import Field
from typing import TYPE_CHECKING, Any, Callable, MutableMapping

from ._hooks import HooksMixin
from ._members import MembersMixin
from .._utils import asdict as _asdict

DictFactory = Callable[[], MutableMapping[str, Any]]
MutableDict = MutableMapping[str, Any]

if TYPE_CHECKING:
    from ..types import DictFactory, MutableDict


class Corbel(HooksMixin, MembersMixin):
    """
    Base mixin for dataclasses providing utility methods and caching.

    Features:
      - Cached `asdict` results for efficient dictionary conversions.
      - Cached dataclass `fields` and field names for introspection.
      - Cached properties and property names for repeated access.
      - Automatic cache invalidation when a tracked field is updated.
      - Supports introspection of fields and properties for validation and updates.
    """

    __corbel_validation: bool = True
    __corbel_asdict: MutableDict | None = None
    __corbel_dirty_fields = dict[str, Field]()

    def __post_init__(
        self,
    ):
        """
        Initialize internal caches and enable validation after dataclass init.
        """
        self.__corbel_validation = True
        self.__corbel_asdict = None
        self.__corbel_dirty_fields = dict[str, Field]()

        super().__post_init__()

    def _corbel_on_validation(
        self,
        field: Field,
        value: Any,
        *,
        error: tuple[str, Exception | None] | None = None,
    ) -> None:
        """
        Hook called during field validation.

        Removes the field from the dirty set regardless of validation outcome.

        :param field:
            The dataclass field being validated.
        :param value:
            The value that was validated.
        :param error:
            Optional tuple containing a validation error message and the exception
            that was raised, if any.
        """
        if field.name in self.__corbel_dirty_fields:
            del self.__corbel_dirty_fields[field.name]

    def _corbel_on_field_update(
        self,
        field: Field,
        value: Any,
        old_value: Any,
    ) -> None:
        """
        Hook called when a field is updated.

        Clears relevant caches and marks the field as dirty.

        :param field:
            The dataclass field being updated.
        :param value:
            The new value assigned to the field.
        :param old_value:
            The previous value of the field.
        """
        self.__corbel_asdict = None
        self.__corbel_dirty_fields[field.name] = field

    def asdict(
        self,
        *,
        dict_factory: DictFactory = dict,
        include_private: bool = False,
        refresh: bool = False,
    ) -> MutableDict:
        """
        Return a dictionary representation of the instance.

        Caches the result for efficiency. Supports forced refresh to recompute
        the dictionary.

        :param dict_factory:
            Callable used to construct the resulting dictionary.
        :param include_private:
            Include private attributes if True.
        :param refresh:
            If True, recompute the dictionary ignoring the cache.
        :return:
            Dictionary mapping field names to current values.
        """
        if refresh or getattr(self, "__corbel_asdict", None) is None:
            self.__corbel_asdict = _asdict(
                self,
                dict_factory=dict_factory,
                include_private=include_private,
            )

        assert self.__corbel_asdict is not None
        return self.__corbel_asdict

    @property
    def _corbel_dirty_fields(
        self,
    ) -> dict[str, Field]:
        """
        Return the set of fields that have been modified since initialization.

        :return:
            Dictionary mapping field names to Field objects that have been modified.
        """
        return self.__corbel_dirty_fields

    @property
    def _corbel_validation(
        self,
    ) -> bool:
        """
        Indicates whether field validation is enabled for this instance.

        :return:
            True if validation is enabled.
        """
        return self.__corbel_validation

    @_corbel_validation.setter
    def _corbel_validation(
        self,
        value: bool,
    ) -> None:
        """
        Enable or disable field validation for this instance.

        :param value:
            True to enable validation, False to disable.
        """
        self.__corbel_validation = value


__all__ = ("Corbel",)

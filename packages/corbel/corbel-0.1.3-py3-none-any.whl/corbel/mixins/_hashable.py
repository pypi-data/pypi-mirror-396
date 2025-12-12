from __future__ import annotations

from typing import TYPE_CHECKING

from ._corbel import Corbel

if TYPE_CHECKING:
    from dataclasses import Field
    from typing import Any


class Hashable(Corbel):
    """
    Mixin for dataclasses that provides a hash implementation based on field values.

    Enables instances to be used as dictionary keys or stored in sets.
    """

    __corbel_hash: int | None = None

    def _corbel_on_field_update(
        self,
        field: Field,
        value: Any,
        old_value: Any,
    ) -> None:
        """
        Invalidate cached hash when a field value is updated.

        :param field:
            The dataclass field that was updated.
        :param value:
            The new value assigned to the field.
        :param old_value:
            The previous value of the field.
        """
        super()._corbel_on_field_update(field, value, old_value)
        self.__corbel_hash = None

    def __hash__(
        self,
    ) -> int:
        """
        Compute a hash value for the instance.

        The hash is derived from the tuple of the instance's current field values.
        Caches the result to avoid recomputation.

        :return:
            Integer hash of the instance.
        """
        if self.__corbel_hash is None:
            self.__corbel_hash = hash(
                tuple(getattr(self, name) for name in self.corbel_members())
            )

        return self.__corbel_hash


__all__ = ("Hashable",)

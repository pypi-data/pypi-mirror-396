from __future__ import annotations

from functools import total_ordering

from ._corbel import Corbel


@total_ordering
class Comparable(Corbel):
    """
    Mixin for dataclasses that provides comparison operations based on field values.

    Uses `asdict()` to compare instances. Supports equality and ordering.
    """

    def __eq__(
        self,
        other: object,
    ) -> bool:
        """
        Check equality with another instance of the same type.

        Two instances are considered equal if all their fields have equal values.

        :param other:
            Object to compare against.
        :return:
            True if equal, False otherwise.
        """
        if not isinstance(other, type(self)):
            return NotImplemented

        for name in self.corbel_members():
            if getattr(self, name) != getattr(other, name):
                return False

        return True

    def __lt__(
        self,
        other: object,
    ) -> bool:
        """
        Compare this instance with another instance of the same type for ordering.

        Comparison is done lexicographically based on the tuple of field values.

        :param other:
            Object to compare against.
        :return:
            True if this instance is less than `other`, False otherwise.
        """
        if not isinstance(other, type(self)):
            return NotImplemented

        for name in self.corbel_members():
            a, b = getattr(self, name), getattr(other, name)

            if a == b:
                continue

            return a < b

        return False


__all__ = ("Comparable",)

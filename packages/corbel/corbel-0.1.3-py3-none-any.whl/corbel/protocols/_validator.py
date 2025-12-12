from __future__ import annotations

from typing import Protocol, TypeVar


T = TypeVar("T")


class ValidatorProtocol(Protocol):
    """
    Protocol for callable objects that validate a value.

    Implementers should provide a `__call__` method that takes a value
    and returns True if the value is valid, False otherwise.
    """

    def __call__(
        self,
        value: T,
    ) -> bool:
        """
        Validate a value.

        :param value:
            The value to validate.
        :return:
            True if the value is valid, False otherwise.
        """
        ...


__all__ = ("ValidatorProtocol",)

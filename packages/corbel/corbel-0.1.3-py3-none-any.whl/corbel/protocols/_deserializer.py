from __future__ import annotations

from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


class DeserializerProtocol(Protocol):
    """
    Protocol for callable objects that deserialize a value into a specific type.

    Implementers should provide a `__call__` method that takes a value and
    an optional type hint, and returns the deserialized value.
    """

    def __call__(
        self,
        value: Any,
        type_hint: type[Any] | str | Any,
    ) -> Any:
        """
        Deserialize a value into the specified type.

        :param value:
            The value to deserialize.
        :param type_hint:
            The expected type or type hint for the value.
        :return:
            The deserialized value.
        """
        ...


__all__ = ("DeserializerProtocol",)

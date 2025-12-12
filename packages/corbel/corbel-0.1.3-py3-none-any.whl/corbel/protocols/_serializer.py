from __future__ import annotations

from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


class SerializerProtocol(Protocol):
    """
    Protocol for callable objects that serialize a value.

    Implementers should provide a `__call__` method that takes a value and
    returns a serialized representation suitable for JSON or dict conversion.
    """

    def __call__(
        self,
        value: Any,
    ) -> Any:
        """
        Serialize a value.

        :param value:
            The value to serialize.
        :return:
            Serialized representation of the value.
        """
        ...


__all__ = ("SerializerProtocol",)

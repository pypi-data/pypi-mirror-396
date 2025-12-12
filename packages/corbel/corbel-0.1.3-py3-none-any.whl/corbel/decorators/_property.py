from __future__ import annotations

from typing import TYPE_CHECKING

from .._objects import CorbelProperty

if TYPE_CHECKING:
    from typing import Any, Callable

    from ..protocols import DeserializerProtocol, SerializerProtocol, ValidatorProtocol


def corbel_property(
    *,
    json: dict[str, Any] | None = None,
    ignore: bool = False,
    allow_none: bool = False,
    validator: ValidatorProtocol | None = None,
    serializer: SerializerProtocol | None = None,
    deserializer: DeserializerProtocol | None = None,
) -> Callable[[Callable[..., Any]], CorbelProperty]:
    """
    Decorator similar to @property, but attaches Corbel metadata.

    Supports standard property behavior including @x.setter and @x.deleter.
    Allows custom validation, serialization, and deserialization.

    :param json:
        Optional dictionary for JSON-related metadata.
    :param ignore:
        If True, this property will be ignored during serialization.
    :param allow_none:
        If True, the property can accept None as a valid value.
    :param validator:
        Optional callable that validates the property's value.
    :param serializer:
        Optional callable to serialize the property's value.
    :param deserializer:
        Optional callable to deserialize input into the property's value.
    :return:
        A CorbelProperty wrapping the decorated function.
    """

    def decorator(
        func: Callable[..., Any],
    ) -> CorbelProperty:
        return CorbelProperty(
            func,
            json=json,
            ignore=ignore,
            allow_none=allow_none,
            validator=validator,
            serializer=serializer,
            deserializer=deserializer,
        )

    return decorator


__all__ = ("corbel_property",)

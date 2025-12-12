from __future__ import annotations

from types import UnionType
from typing import Any, get_args, get_origin, Union

from ._deserialize_obj import deserialize_obj


def deserialize_value(
    value: Any,
    type_hint: Any,
) -> Any:
    """
    Deserialize a value into the expected type, including optional types.

    Supports standard types, complex types, and optional types represented as
    Union with None. Delegates complex type deserialization to
    :func:`deserialize_obj`.

    :param value:
        The value to deserialize.
    :param type_hint:
        The expected type of the value, including optional or Union types.
    :return:
        The deserialized value cast to the expected type.
    :rtype: Any
    :raises TypeError:
        If the value does not match any type in a Union.
    """
    if type_hint is Any:
        return value

    if type_hint is None:
        return value

    origin = get_origin(type_hint)
    types = get_args(type_hint)

    # Non-generic type
    if origin is None:
        if value is None and type_hint is type(None):
            return None
        if isinstance(value, type_hint):
            return value

    if origin in (Union, UnionType):
        if value is None and type(None) in types:
            return None

        error = None

        for arg in types:
            try:
                return deserialize_value(value, arg)
            except Exception as e:
                error = e

        raise TypeError(
            f"Value {value!r} does not match any type in {type_hint}"
        ) from error

    return deserialize_obj(value, type_hint, origin, deserialize_value)


__all__ = ("deserialize_value",)

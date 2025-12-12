from __future__ import annotations

from dataclasses import is_dataclass
from datetime import datetime, date, time
from enum import Enum
from typing import Any, get_args, TYPE_CHECKING
from uuid import UUID

from ._deserialize_dataclass import deserialize_dataclass

if TYPE_CHECKING:
    from typing import Callable, Type


TYPE_TRANSFORMERS: dict[Type, Callable[[Any], Any]] = {
    datetime: datetime.fromisoformat,
    date: date.fromisoformat,
    time: time.fromisoformat,
    UUID: UUID,
}


def deserialize_obj(
    value: Any,
    expected_type: Any,
    origin: Any,
    deserialize_fn: Callable[[Any, Any], Any],
) -> Any:
    """
    Deserialize a value into the specified type.

    Handles nested dataclasses, lists, tuples, dictionaries, enums, datetime,
    date, time, UUID, and other standard types. Uses the provided
    `deserialize_fn` recursively for complex types.

    :param value:
        The value to deserialize.
    :param expected_type:
        The type into which the value should be deserialized.
    :param origin:
        The origin type obtained via :func:`typing.get_origin`.
    :param deserialize_fn:
        A callable that deserializes individual elements or fields.
    :return:
        The value deserialized into the specified type.
    :rtype: Any
    """
    if is_dataclass(expected_type):
        return deserialize_dataclass(value, expected_type, deserialize_fn)
    elif origin is list:
        (item_type,) = get_args(expected_type) or (Any,)

        return [deserialize_fn(item, item_type) for item in value]
    elif origin is tuple:
        args = get_args(expected_type) or (Any,)

        return tuple(deserialize_fn(item, typ) for item, typ in zip(value, args))
    elif origin is dict:
        (key_type, value_type) = get_args(expected_type) or (str, Any)

        return {
            deserialize_fn(k, key_type): deserialize_fn(v, value_type)
            for k, v in value.items()
        }
    elif isinstance(expected_type, type) and issubclass(expected_type, Enum):
        return expected_type(value)

    transformer = TYPE_TRANSFORMERS.get(expected_type)

    if callable(transformer):
        return transformer(value)

    return expected_type(value) if expected_type is not Any else value


__all__ = ("deserialize_obj",)

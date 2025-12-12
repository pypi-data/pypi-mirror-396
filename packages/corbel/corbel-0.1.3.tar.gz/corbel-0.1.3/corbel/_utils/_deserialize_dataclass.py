from __future__ import annotations

from dataclasses import fields as _fields
from typing import TYPE_CHECKING

from ..errors import DeserializeError
from ..protocols import CorbelDataclass

if TYPE_CHECKING:
    from typing import Any, Callable


def deserialize_dataclass(
    value: Any,
    expected_type: Any,
    deserialize_fn: Callable[[Any, Any], Any],
) -> CorbelDataclass:
    """
    Deserialize a dictionary into a Corbel dataclass instance.

    This function converts a dictionary into an instance of the specified
    dataclass type. If the dataclass has a custom `from_dict` method, it will
    be used; otherwise, the function falls back to standard field-based
    deserialization. Each field value is processed using the provided
    `deserialize_fn`.

    :param value:
        The dictionary to deserialize.
    :param expected_type:
        The dataclass type to produce.
    :param deserialize_fn:
        A callable that deserializes individual field values. Receives the
        raw value and the expected field type.
    :return:
        An instance of the specified Corbel dataclass type.
    :rtype: CorbelDataclass
    :raises DeserializeError:
        If `value` is not a dictionary.
    """
    if not isinstance(value, dict):
        raise DeserializeError(
            (
                f"Expected a dict to deserialize {expected_type}, "
                f"got {type(value).__name__}"
            ),
            field=None,
            value=value,
        )

    if not hasattr(expected_type, "from_dict"):
        fields = (
            expected_type.corbel_fields
            if hasattr(expected_type, "corbel_fields")
            else _fields(expected_type)
        )

        return expected_type(
            **{f.name: deserialize_fn(value[f.name], f.type) for f in fields}
        )

    return expected_type.from_dict(value)


__all__ = ("deserialize_dataclass",)

from __future__ import annotations

from typing import TYPE_CHECKING

from ._deserialize_value import deserialize_value
from ._corbel_metadata import corbel_metadata
from ..errors import DeserializeError
from ..protocols import DeserializerProtocol

if TYPE_CHECKING:
    from dataclasses import Field
    from typing import Any


def deserialize_field(field: Field, value: Any, type_hint: Any) -> Any:
    """
    Deserialize a value for a specific dataclass field.

    If a custom deserializer is defined in the field's metadata, it is used.
    Otherwise, the value is deserialized using the default
    :func:`deserialize_value`. Any exception during deserialization is wrapped
    in a :exc:`DeserializeError`.

    :param field:
        The dataclass field being deserialized.
    :param value:
        The raw value to deserialize.
    :param type_hint:
        The expected type of the field, used for type-aware deserialization.
    :return:
        The deserialized value for the field.
    :rtype: Any
    :raises DeserializeError:
        If deserialization fails for any reason.
    """
    try:
        deserializer: DeserializerProtocol = corbel_metadata(
            field, "deserializer", deserialize_value
        )

        return deserializer(value, type_hint)
    except Exception as e:
        raise DeserializeError(
            f"Failed to deserialize field '{field.name}'",
            field=field,
            value=value,
            error=e,
        ) from e


__all__ = ("deserialize_field",)

from __future__ import annotations

from typing import Any, get_type_hints, TYPE_CHECKING

from ._default_value import default_value
from ._deserialize_field import deserialize_field
from ._fields import fields
from ._is_required import is_required
from ._corbel_metadata import corbel_metadata
from ..errors import DeserializeError

if TYPE_CHECKING:
    from ..types import TCorbelDataclass


def from_dict(
    cls: type[TCorbelDataclass],
    data: dict[str, Any],
) -> TCorbelDataclass:
    """
    Deserialize a dictionary into a dataclass instance.

    Processes each field in the class, applying default values or factories
    when fields are missing, and using :func:`deserialize_field` for
    deserialization. Required fields missing in the input raise
    :exc:`DeserializeError`.

    :param cls:
        The dataclass type to instantiate.
    :param data:
        A dictionary containing field values.
    :return:
        An instance of the dataclass populated with the provided data.
    :rtype: TCorbelDataclass
    :raises DeserializeError:
        If a required field is missing or default generation fails.
    """
    kwargs = dict[str, Any]()
    type_hints = get_type_hints(cls)

    for field in fields(cls):
        if corbel_metadata(field, "ignore", False):
            continue

        if field.name in data:
            kwargs[field.name] = deserialize_field(
                field,
                data[field.name],
                type_hints[field.name],
            )
        elif is_required(field):
            raise DeserializeError(
                f"Missing required field '{field.name}'",
                field=field,
            )
        else:
            try:
                kwargs[field.name] = default_value(field)
            except Exception as e:
                raise DeserializeError(
                    f"Failed to generate default for field '{field.name}'",
                    field=field,
                    value=None,
                    error=e,
                ) from e

    return cls(**kwargs)


__all__ = ("from_dict",)

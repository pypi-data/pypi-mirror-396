from __future__ import annotations

from json import loads, JSONDecodeError
from typing import Any, TYPE_CHECKING

from ._fields import fields
from ._from_dict import from_dict
from ._resolve_field_key import resolve_field_key
from ..errors import DeserializeError

if TYPE_CHECKING:
    from json import JSONDecoder
    from typing import Callable, Type

    from ..types import TCorbelDataclass


def from_json(
    cls: type[TCorbelDataclass],
    s: str | bytes | bytearray,
    *,
    wrapper: str | None = None,
    json_cls: Type[JSONDecoder] | None = None,
    object_hook: Callable[[dict[Any, Any]], Any] | None = None,
    parse_float: Callable[[str], Any] | None = None,
    parse_int: Callable[[str], Any] | None = None,
    parse_constant: Callable[[str], Any] | None = None,
    object_hook_pairs: Callable[[list[tuple[Any, Any]]], Any] | None = None,
) -> TCorbelDataclass:
    """
    Deserialize a JSON string, bytes, or bytearray into a dataclass instance.

    Supports optional top-level wrapper keys and custom JSON decoder hooks.
    Each field key is resolved via :func:`resolve_field_key` and deserialized
    using :func:`from_dict`. Duplicate keys in JSON raise an error.

    :param cls:
        The dataclass type to instantiate.
    :param s:
        JSON string, bytes, or bytearray to deserialize.
    :param wrapper:
        Optional top-level key to extract data from the JSON.
    :param json_cls:
        Optional custom JSON decoder class.
    :param object_hook:
        Optional callable for custom object decoding.
    :param parse_float:
        Optional callable for decoding float values.
    :param parse_int:
        Optional callable for decoding integer values.
    :param parse_constant:
        Optional callable for decoding constants (NaN, Infinity, etc.).
    :param object_pairs_hook:
        Optional callable for decoding key-value pairs as a list of tuples.
    :return:
        An instance of `cls` populated with the deserialized data.
    :rtype: TCorbelDataclass
    :raises DeserializeError:
        If JSON decoding fails or field deserialization fails.
    """
    try:
        _data = loads(
            s,
            cls=json_cls,
            object_hook=object_hook,
            parse_float=parse_float,
            parse_int=parse_int,
            parse_constant=parse_constant,
            object_pairs_hook=object_hook_pairs,
        )

        _data = _data[wrapper] if wrapper else _data
        data = dict[str, Any]()
        used_keys = set[str]()

        for field in fields(cls):
            key = resolve_field_key(field, _data)

            if key not in _data:
                continue

            if key in used_keys:
                raise KeyError(f"Duplicate key '{key}' for field '{field.name}'")

            used_keys.add(key)
            data[field.name] = _data[key]

        return from_dict(cls, data)
    except (KeyError, JSONDecodeError) as e:
        raise DeserializeError(
            f"Failed to deserialize JSON to '{cls.__name__}'", error=e
        ) from e


__all__ = ("from_json",)

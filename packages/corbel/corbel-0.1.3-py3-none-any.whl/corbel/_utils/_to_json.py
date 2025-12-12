from __future__ import annotations

from json import dumps
from typing import TYPE_CHECKING

from ._to_dict import to_dict
from ._corbel_metadata import corbel_metadata
from ..enums import Include

if TYPE_CHECKING:
    from json import JSONEncoder
    from typing import Any, Callable, Type

    from ..types import DictFactory, ListFactory, TSerializable


def to_json(
    self: TSerializable,
    include: Include,
    *,
    wrapper: str | None = None,
    include_properties: bool = True,
    include_private: bool = False,
    dict_factory: DictFactory = dict,
    list_factory: ListFactory = list,
    skip_keys: bool = False,
    ensure_ascii: bool = True,
    check_circular: bool = True,
    allow_nan: bool = True,
    json_cls: Type[JSONEncoder] | None = None,
    indent: int | None = None,
    separators: tuple[str, str] | None = None,
    default: Callable[[Any], Any] | None = None,
    sort_keys: bool = False,
    **kwargs: Any,
) -> str:
    """
    Serialize a dataclass instance to a JSON string.

    Applies inclusion rules, optional key overrides, and standard JSON
    serialization options. Optionally wraps the resulting dictionary under
    a single key.

    :param self:
        The dataclass instance to serialize.
    :param include:
        Inclusion rule specifying which fields to include.
    :param wrapper:
        Optional key under which to wrap the serialized data.
    :param include_properties:
        Include properties as fields if True.
    :param include_private:
        Include private members (starting with '_') if True.
    :param dict_factory:
        Factory function to create dictionaries.
    :param list_factory:
        Factory function to create lists.
    :param skip_keys:
        Skip keys that cannot be serialized if True.
    :param ensure_ascii:
        Escape non-ASCII characters if True.
    :param check_circular:
        Check for circular references.
    :param allow_nan:
        Allow NaN, Infinity, and -Infinity in output.
    :param json_cls:
        Optional custom JSON encoder class.
    :param indent:
        Optional indentation level.
    :param separators:
        Optional separators for JSON output.
    :param default:
        Optional callable for non-serializable objects.
    :param sort_keys:
        Sort dictionary keys if True.
    :param kwargs:
        Additional keyword arguments for the JSON encoder.
    :return:
        JSON string representation of the instance.
    :rtype: str
    """
    raw_data = to_dict(
        self,
        include,
        include_properties=include_properties,
        include_private=include_private,
        dict_factory=dict_factory,
        list_factory=list_factory,
    )
    members = self.corbel_members(
        include_properties=include_properties,
        include_private=include_private,
    )
    data = dict_factory()

    for name, member in members.items():
        if name not in raw_data:
            continue

        key = corbel_metadata(member, "json.key", name)

        if name in raw_data:
            data[key] = raw_data[name]

    data = {wrapper: data} if wrapper else data

    return dumps(
        data,
        skipkeys=skip_keys,
        ensure_ascii=ensure_ascii,
        check_circular=check_circular,
        allow_nan=allow_nan,
        cls=json_cls,
        indent=indent,
        separators=separators,
        default=default,
        sort_keys=sort_keys,
        **kwargs,
    )


__all__ = ("to_json",)

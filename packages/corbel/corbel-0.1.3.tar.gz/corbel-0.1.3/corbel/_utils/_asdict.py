from __future__ import annotations

from typing import TYPE_CHECKING

from ._capture_member import capture_member

if TYPE_CHECKING:
    from typing import Any, MutableMapping

    from ..types import DictFactory, ListFactory, TCorbelMixin


def asdict(
    obj: TCorbelMixin,
    *,
    include_properties: bool = True,
    include_private: bool = False,
    dict_factory: DictFactory = dict,
    list_factory: ListFactory = list,
) -> MutableMapping[str, Any]:
    """
    Convert a Corbel dataclass-like object into a dictionary representation.

    This function traverses the object's fields and properties, optionally
    including private members and computed properties. Nested Corbel dataclasses
    and collections are processed recursively using the provided factory
    functions.

    :param obj:
        The Corbel dataclass-like instance to serialize.
    :param include_properties:
        Whether to include ``@property`` attributes in the output. Defaults to
        ``True``.
    :param include_private:
        Whether to include members whose names start with ``_``. Defaults to
        ``False``.
    :param dict_factory:
        A callable used to construct the resulting dictionary. Defaults to
        :class:`dict`.
    :param list_factory:
        A callable used to construct lists within the dictionary. Defaults to
        :class:`list`.
    :return:
        A mapping of member names to values, with nested dataclasses and
        collections represented as dictionaries and lists.
    :rtype: MutableMapping[str, Any]
    """
    data = dict_factory()
    members = obj.corbel_members(
        include_properties=include_properties,
        include_private=include_private,
    )

    for name, member in members.items():
        value = getattr(obj, name, None)
        data[name] = capture_member(
            member,
            value,
            dict_factory=dict_factory,
            list_factory=list_factory,
        )

    return data


__all__ = ("asdict",)

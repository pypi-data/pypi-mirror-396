from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import cast, TYPE_CHECKING

from ..protocols import CorbelDataclass

if TYPE_CHECKING:
    from typing import Any

    from ..types import DictFactory, ListFactory, Member, Stack


def capture_obj(
    member: Member,
    value: Any,
    stack: Stack,
    *,
    dict_factory: DictFactory = dict,
    list_factory: ListFactory = list,
) -> Any:
    """
    Recursively capture an object's value for serialization.

    This function processes dataclasses, lists, tuples, and dictionaries by
    pushing elements onto a stack for iterative depth-first traversal. Objects
    are transformed into a representation suitable for dictionary or JSON
    output.

    :param member:
        The member (field or property) associated with the value.
    :param value:
        The current value to capture.
    :param stack:
        The stack used for iterative traversal of nested structures.
    :param dict_factory:
        A callable used to construct dictionaries. Defaults to :class:`dict`.
    :param list_factory:
        A callable used to construct lists. Defaults to :class:`list`.
    :return:
        A serialized value suitable for inclusion in a dictionary or JSON
        representation.
    :rtype: Any
    """
    if is_dataclass(value):
        if hasattr(value, "asdict"):
            return value.asdict(dict_factory=dict_factory)
        else:
            return asdict(cast(CorbelDataclass, value))
    elif isinstance(value, (list, tuple)):
        items = list_factory()

        for item in reversed(value):
            stack.append((member, item, items, "list_item", dict_factory, list_factory))

        return items
    elif isinstance(value, dict):
        data = dict_factory()

        for k, v in value.items():
            stack.append((member, v, data, k, dict_factory, list_factory))

        return data
    else:
        return value


__all__ = ("capture_obj",)

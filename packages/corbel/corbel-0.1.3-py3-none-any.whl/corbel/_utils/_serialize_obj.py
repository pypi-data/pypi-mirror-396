from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import datetime, date, time
from enum import Enum
from typing import cast, TYPE_CHECKING
from uuid import UUID

from ..protocols import CorbelDataclass

if TYPE_CHECKING:
    from typing import Any

    from ..types import DictFactory, ListFactory, Member, Stack


def serialize_obj(
    member: Member,
    value: Any,
    stack: Stack,
    *,
    dict_factory: DictFactory = dict,
    list_factory: ListFactory = list,
) -> Any:
    """
    Serialize an object into a JSON-compatible structure recursively.

    Supports dataclasses, lists, tuples, dictionaries, Enums, datetime/date/time
    objects, and UUIDs. Uses a stack to track nested elements and prevent deep
    recursion.

    :param member:
        The dataclass field or member being serialized.
    :param value:
        The value to serialize.
    :param stack:
        Stack used to track nested serialization tasks.
    :param dict_factory:
        Factory function to create dictionaries.
    :param list_factory:
        Factory function to create lists.
    :return:
        Serialized representation suitable for JSON encoding.
    """
    if is_dataclass(value):
        if hasattr(value, "to_dict"):
            return value.to_dict()
        elif hasattr(value, "asdict"):
            return value.asdict()
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
    elif isinstance(value, Enum):
        return value.value
    elif isinstance(value, (datetime, date, time)):
        return value.isoformat()
    elif isinstance(value, UUID):
        return str(value)
    else:
        return value


__all__ = ("serialize_obj",)

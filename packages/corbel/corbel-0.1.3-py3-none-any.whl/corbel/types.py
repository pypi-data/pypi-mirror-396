from __future__ import annotations

from dataclasses import Field
from typing import Any, Callable, MutableMapping, TypeVar

from .protocols import CorbelDataclass
from .mixins import Serializable, Corbel


Member = Field | property
"""
Type alias for a dataclass member, which can be either a Field or a property.
"""

# Standard mutable dictionary type
MutableDict = MutableMapping[str, Any]
"""
Type alias for a standard mutable dictionary mapping strings to any value.
"""

DictFactory = Callable[[], MutableDict]
"""
Callable that returns a new mutable dictionary.
"""

ListFactory = Callable[[], list[Any]]
"""
Callable that returns a new list.
"""

StackParent = list[Any] | MutableDict | None
"""
Type representing the parent object in a serialization stack:
can be a list, a dictionary, or None.
"""

StackKey = str | Any | None
"""
Type representing the key or index in a serialization stack:
can be a string, any value, or None.
"""

Stack = list[tuple[Member, Any, StackParent, StackKey, DictFactory, ListFactory]]
"""
A stack for tracking members during recursive serialization.

Each entry is a tuple containing:
- member: The dataclass member (Field or property)
- value: The current value of the member
- parent: The parent container (list, dict, or None)
- key: The key/index in the parent container
- dict_factory: Callable to construct new dictionaries
- list_factory: Callable to construct new lists
"""

TCorbelDataclass = TypeVar("TCorbelDataclass", bound=CorbelDataclass)
"""
Generic type variable bound to any class implementing CorbelDataclass.
"""

TSerializable = TypeVar("TSerializable", bound=Serializable)
"""
Generic type variable bound to any class implementing Serializable.
"""

TCorbelMixin = TypeVar("TCorbelMixin", bound=Corbel)
"""
Generic type variable bound to any class implementing Corbel.
"""

__all__ = (
    "DictFactory",
    "ListFactory",
    "Member",
    "MutableDict",
    "Stack",
    "TCorbelDataclass",
    "TSerializable",
    "TCorbelMixin",
)

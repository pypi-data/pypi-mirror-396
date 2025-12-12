from __future__ import annotations

from typing import Protocol, runtime_checkable, TYPE_CHECKING

if TYPE_CHECKING:
    from dataclasses import Field
    from typing import Any, ClassVar


@runtime_checkable
class CorbelDataclass(Protocol):
    """
    Protocol representing dataclass-like objects with introspection utilities.

    Provides a consistent interface for accessing fields and members of
    dataclass instances, enabling serialization, validation, and updates
    in Corbel-based mixins.

    Attributes:
        __dataclass_fields__:
            Class variable mapping field names to dataclasses.Field objects.
            Provides standard dataclass introspection.
    """

    __mro__: tuple[type, Any]
    __bases__: tuple[type, ...]

    __dataclass_fields__: ClassVar[dict[str, Field[Any]]]


__all__ = ("CorbelDataclass",)

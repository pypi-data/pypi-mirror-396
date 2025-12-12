from __future__ import annotations

from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

    from ..types import DictFactory, ListFactory, Member, Stack


class MemberCaptureProtocol(Protocol):
    """
    Protocol for functions that capture a member's value for serialization.

    Allows custom logic for converting dataclass fields, properties, or other
    objects into a serializable representation, handling nested structures
    via a stack.
    """

    def __call__(
        self,
        member: Member,
        value: Any,
        stack: Stack,
        *,
        dict_factory: DictFactory,
        list_factory: ListFactory,
    ) -> Any:
        """
        Capture and serialize a member's value.

        :param member:
            The member (field or property) being processed.
        :param value:
            Current value of the member.
        :param stack:
            Stack used for iterative depth-first traversal of nested objects.
        :param dict_factory:
            Callable to construct dictionaries.
        :param list_factory:
            Callable to construct lists.
        :return:
            Serialized value suitable for dict or JSON representation.
        """
        ...


__all__ = ("MemberCaptureProtocol",)

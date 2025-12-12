from __future__ import annotations

from typing import TYPE_CHECKING

from ._default_value import default_value
from ..enums import Include
from ..errors import InclusionError

if TYPE_CHECKING:
    from ..types import Member


def include_member(
    member: Member,
    value: object,
    include: Include,
) -> bool:
    """
    Determine whether a dataclass member should be included during serialization.

    Applies the inclusion rules defined in the :class:`Include` enum:

      - ALWAYS: Always include the member.
      - NON_NONE: Include only if the value is not None.
      - NON_EMPTY: Include if the value is truthy (non-empty for strings,
        collections, etc.).
      - NON_DEFAULT: Include only if the value differs from the field's default.

    :param member:
        The dataclass field or property to evaluate.
    :param value:
        Current value of the member.
    :param include:
        Inclusion rule to apply.
    :return:
        True if the member satisfies the inclusion rule, False otherwise.
    :rtype: bool
    :raises InclusionError:
        If NON_DEFAULT is used on a property or an unknown inclusion rule is
        provided.
    """
    if include is Include.ALWAYS:
        return True
    if include is Include.NON_NONE:
        return value is not None
    if include is Include.NON_EMPTY:
        if value is None:
            return False

        if isinstance(value, (str, bytes, list, tuple, set, dict)):
            return bool(value)

        return True
    if include is Include.NON_DEFAULT:
        if isinstance(member, property):
            raise InclusionError(
                "Cannot use Include.NON_DEFAULT with include_properties=True"
            )

        default_val = default_value(member)
        return value != default_val

    raise InclusionError(f"Unhandled Include rule: {include}", include=include)


__all__ = ("include_member",)

from __future__ import annotations

from dataclasses import MISSING
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dataclasses import Field


def is_required(
    field: Field,
) -> bool:
    """
    Determine whether a dataclass field is required.

    A field is considered required if it has neither a default value nor a
    default factory.

    :param field:
        The dataclass field to check.
    :return:
        True if the field is required, False otherwise.
    :rtype: bool
    """
    return field.default is MISSING and field.default_factory is MISSING


__all__ = ("is_required",)

from __future__ import annotations

from dataclasses import fields as _fields
from functools import cached_property
from typing import cast, TYPE_CHECKING

from ..protocols import CorbelDataclass

if TYPE_CHECKING:
    from dataclasses import Field
    from typing import Type

    from ..types import TCorbelDataclass


def fields(
    cls: Type[TCorbelDataclass],
) -> tuple[Field, ...]:
    """
    Retrieve the dataclass fields for a Corbel dataclass type.

    Returns the ``corbel_fields`` attribute if present, otherwise falls back
    to standard :func:`dataclasses.fields`.

    :param cls:
        The dataclass type to inspect.
    :return:
        A tuple of :class:`dataclasses.Field` objects representing the fields
        of the class.
    :rtype: tuple[Field, ...]
    """
    corbel_fields = getattr(cast(CorbelDataclass, cls), "corbel_fields", None)

    if isinstance(corbel_fields, cached_property):
        corbel_fields = None

    if isinstance(corbel_fields, tuple):
        return corbel_fields

    return _fields(cls)


__all__ = ("fields",)

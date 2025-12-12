from __future__ import annotations

from dataclasses import MISSING
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dataclasses import Field
    from typing import Any


def default_value(
    field: Field,
) -> Any:
    """
    Retrieve the default value for a dataclass field.

    Returns the value produced by `default_factory` if defined. If not, returns
    the `default` value. Returns ``None`` if neither is set.

    :param field:
        The dataclass field whose default is to be retrieved.
    :return:
        The default value for the field, or ``None`` if no default exists.
    :rtype: Any
    """
    if field.default_factory is not MISSING:
        return field.default_factory()
    elif field.default is not MISSING:
        return field.default
    else:
        return None


__all__ = ("default_value",)

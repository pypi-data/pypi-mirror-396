from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Callable


def field(
    *,
    default: Any = dataclasses.MISSING,
    default_factory: Any = dataclasses.MISSING,
    init: bool = True,
    repr: bool = True,
    hash: bool | None = None,
    compare: bool = True,
    metadata: dict[str, Any] | None = None,
    json: dict[str, Any] | None = None,
    validator: Callable[[Any], bool] | None = None,
    allow_none: bool = False,
    corbel: dict[str, Any] | None = None,
    **kwargs: Any,
):
    """
    Custom dataclass field wrapper with Corbel-specific enhancements.

    Extends :func:`dataclasses.field` to support additional metadata for JSON
    serialization, field validation, and Corbel-specific features.

    Features:
      - JSON serialization metadata via `json`.
      - Field validation via `validator`.
      - Optional allowance of None values via `allow_none`.
      - Corbel-specific metadata via `corbel`.
      - Fully compatible with standard dataclass arguments (`default`, `init`,
        `repr`, `hash`, `compare`, `metadata`).

    :param default:
        Default value for the field.
    :param default_factory:
        Factory function to generate default values.
    :param init:
        Include the field in the generated ``__init__`` method.
    :param repr:
        Include the field in the generated ``__repr__`` method.
    :param hash:
        Include the field in the generated ``__hash__`` method.
    :param compare:
        Include the field in comparison methods.
    :param metadata:
        Additional metadata dictionary.
    :param json:
        Optional JSON-related metadata stored under
        ``metadata['corbel']['json']``.
    :param validator:
        Optional callable to validate field values.
    :param allow_none:
        If True, allow the field to be None.
    :param corbel:
        Optional dictionary for additional Corbel-specific metadata.
    :param kwargs:
        Additional keyword arguments passed to :func:`dataclasses.field`.
    :return:
        A :class:`dataclasses.Field` object enhanced with Corbel metadata.
    :rtype: dataclasses.Field
    """
    metadata = metadata or {}

    metadata["corbel"] = corbel or {}
    metadata["corbel"].update(
        {
            "json": json or {},
            "allow_none": allow_none,
            "validator": validator,
        }
    )

    args: dict[str, Any] = dict(
        init=init,
        repr=repr,
        hash=hash,
        compare=compare,
        metadata=metadata,
        **kwargs,
    )

    if default is not dataclasses.MISSING:
        args["default"] = default
    if default_factory is not dataclasses.MISSING:
        args["default_factory"] = default_factory

    return dataclasses.field(**args)

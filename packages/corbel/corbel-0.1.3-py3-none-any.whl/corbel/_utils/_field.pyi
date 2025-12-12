from __future__ import annotations

import dataclasses
from typing import overload, TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Callable, Mapping

@overload
def field(
    *,
    default: Any,
    init: bool = True,
    repr: bool = True,
    hash: bool | None = None,
    compare: bool = True,
    metadata: Mapping[str, Any] | None = None,
    json: dict[str, Any] | None = None,
    validator: Callable[[Any], bool] | None = None,
    allow_none: bool = False,
    corbel: dict[str, Any] | None = None,
    **kwargs: Any,
) -> dataclasses.Field[Any]: ...
@overload
def field(
    *,
    default_factory: Callable[[], Any],
    init: bool = True,
    repr: bool = True,
    hash: bool | None = None,
    compare: bool = True,
    metadata: Mapping[str, Any] | None = None,
    json: dict[str, Any] | None = None,
    validator: Callable[[Any], bool] | None = None,
    allow_none: bool = False,
    corbel: dict[str, Any] | None = None,
    **kwargs: Any,
) -> dataclasses.Field[Any]: ...
@overload
def field(
    *,
    init: bool = True,
    repr: bool = True,
    hash: bool | None = None,
    compare: bool = True,
    metadata: Mapping[str, Any] | None = None,
    json: dict[str, Any] | None = None,
    validator: Callable[[Any], bool] | None = None,
    allow_none: bool = False,
    corbel: dict[str, Any] | None = None,
    **kwargs: Any,
) -> dataclasses.Field[Any]: ...

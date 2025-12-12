from __future__ import annotations

from typing import overload, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable


_T = TypeVar("_T")


@overload
def dataclass(
    cls: None,
    /,
) -> Callable[[type[_T]], type[_T]]: ...


@overload
def dataclass(
    cls: type[_T],
    /,
) -> type[_T]: ...


@overload
def dataclass(
    *,
    init: bool = True,
    repr: bool = True,
    eq: bool = True,
    order: bool = False,
    unsafe_hash: bool = False,
    frozen: bool = False,
    match_args: bool = True,
    kw_only: bool = False,
    slots: bool = False,
    weakref_slot: bool = False,
) -> Callable[[type[_T]], type[_T]]: ...

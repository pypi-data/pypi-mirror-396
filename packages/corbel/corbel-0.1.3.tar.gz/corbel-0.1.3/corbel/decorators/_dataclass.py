from __future__ import annotations

from dataclasses import dataclass as _dataclass

from ..types import TCorbelDataclass
from ..mixins import Corbel


def dataclass(
    cls: type[TCorbelDataclass] | None = None,
    /,
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
) -> TCorbelDataclass:
    def wrap(
        _cls: type[TCorbelDataclass],
    ) -> type[TCorbelDataclass]:
        if Corbel not in _cls.__mro__:
            _cls = type(_cls.__name__, (Corbel, *_cls.__bases__), dict(_cls.__dict__))

        return _dataclass(
            init=init,
            repr=repr,
            eq=eq,
            order=order,
            unsafe_hash=unsafe_hash,
            frozen=frozen,
            match_args=match_args,
            kw_only=kw_only,
            slots=slots,
            weakref_slot=weakref_slot,
        )(_cls)

    return wrap(cls) if cls else wrap


__all__ = ("dataclass",)

from __future__ import annotations

from corbel.mixins._meta import CorbelMeta


class BaseMixin(metaclass=CorbelMeta):
    """
    Base mixin providing the Corbel metaclass for dataclass extensions.
    """

    pass


__all__ = ("BaseMixin",)

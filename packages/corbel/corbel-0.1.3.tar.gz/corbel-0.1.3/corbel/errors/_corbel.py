from __future__ import annotations


class CorbelError(Exception):
    """
    Base exception for errors related to the Corbel dataclass utilities.

    Can be used to catch all custom exceptions raised by Corbel mixins and helpers.
    """

    pass


__all__ = ("CorbelError",)

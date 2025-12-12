from __future__ import annotations

from enum import Enum, auto


class Include(Enum):
    """
    Enum specifying inclusion rules for serialization.

    - ALWAYS: Include all members.
    - NON_NONE: Include members that are not None.
    - NON_EMPTY: Include members that are not empty (e.g., '', [], {}).
    - NON_DEFAULT: Include members whose value differs from the default.
    """

    ALWAYS = auto()
    NON_NONE = auto()
    NON_EMPTY = auto()
    NON_DEFAULT = auto()


__all__ = ("Include",)

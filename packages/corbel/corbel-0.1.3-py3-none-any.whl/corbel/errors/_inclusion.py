from __future__ import annotations

from typing import TYPE_CHECKING

from ._corbel import CorbelError

if TYPE_CHECKING:
    from typing import Any


class InclusionError(CorbelError):
    """
    Error raised when an invalid inclusion rule is used during serialization.

    Can include the invalid Include enum value or custom rule that caused the error.
    """

    def __init__(
        self,
        message: str,
        *,
        include: Any | None = None,
    ):
        """
        Initialize an InclusionError.

        :param message:
            Error message describing the inclusion rule failure.
        :param include:
            The Include enum value or rule that caused the error, if any.
        """
        self._include = include
        super().__init__(message)

    @property
    def include(
        self,
    ) -> Any:
        """
        The Include enum value or rule that caused the error.

        :return:
            The problematic inclusion rule.
        """
        return self._include


__all__ = ("InclusionError",)

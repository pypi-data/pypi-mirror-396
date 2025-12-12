from __future__ import annotations

from typing import TYPE_CHECKING

from ._corbel import CorbelError

if TYPE_CHECKING:
    from typing import Any
    from dataclasses import Field


class DeserializeError(CorbelError):
    """
    Exception raised when deserialization of a dataclass field or instance fails.

    Can include the field, its value, and the original error that caused the failure.
    """

    def __init__(
        self,
        message: str,
        *,
        field: Field | None = None,
        value: Any | None = None,
        error: Exception | None = None,
    ):
        """
        Initialize a DeserializeError.

        :param message:
            Error message describing the deserialization failure.
        :param field:
            Optional dataclass field that caused the failure.
        :param value:
            Optional value that failed to deserialize.
        :param error:
            Optional original exception raised during deserialization.
        """
        self._field = field
        self._value = value
        self._error = error

        super().__init__(message)

    @property
    def field(
        self,
    ) -> Field | None:
        """
        The dataclass field that caused the deserialization error, if any.

        :return:
            `dataclasses.Field` object or None.
        """
        return self._field

    @property
    def value(
        self,
    ) -> Any | None:
        """
        The value that failed to deserialize, if any.

        :return:
            The problematic value or None.
        """
        return self._value

    @property
    def error(
        self,
    ) -> Exception | None:
        """
        The original exception raised during deserialization, if any.

        :return:
            Original exception or None.
        """
        return self._error


__all__ = ("DeserializeError",)

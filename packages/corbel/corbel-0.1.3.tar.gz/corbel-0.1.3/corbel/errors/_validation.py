from __future__ import annotations

from typing import TYPE_CHECKING

from ._corbel import CorbelError

if TYPE_CHECKING:
    from dataclasses import Field
    from typing import Any


class ValidationError(CorbelError):
    """
    Exception raised when validation of a dataclass field fails.

    Contains the field, its value, and optionally the original error.
    """

    def __init__(
        self,
        message: str,
        *,
        field: Field,
        value: Any,
        error: Exception | None = None,
    ):
        """
        Initialize a ValidationError.

        :param message:
            Error message describing the validation failure.
        :param field:
            The dataclass field that failed validation.
        :param value:
            The value of the field that failed validation.
        :param error:
            Optional original exception raised during validation.
        """
        self._field = field
        self._value = value
        self._error = error

        super().__init__(message)

    @property
    def field(
        self,
    ) -> Field:
        """
        The dataclass field that caused the validation error.

        :return:
            `dataclasses.Field` object.
        """
        return self._field

    @property
    def value(
        self,
    ) -> Any:
        """
        The value of the field that failed validation.

        :return:
            The invalid value.
        """
        return self._value

    @property
    def error(
        self,
    ) -> Exception | None:
        """
        The original exception raised during validation, if any.

        :return:
            Original exception or None.
        """
        return self._error


__all__ = ("ValidationError",)

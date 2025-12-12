from __future__ import annotations

from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from dataclasses import Field
    from typing import Any


class HooksProtocol(Protocol):
    """
    Protocol for dataclass-like objects that wish to implement hooks
    for validation and field updates.

    Allows external code or mixins to trigger standardized behavior
    when fields are validated or updated.
    """

    def _corbel_on_validation(
        self,
        field: Field,
        value: Any,
        *,
        error: tuple[str, Exception | None] | None = None,
    ) -> None:
        """
        Called after a field has been validated.

        :param field:
            The dataclass field being validated.
        :param value:
            The value that was validated.
        :param error:
            Optional tuple containing an error message and the
            exception raised, if any.
        """

    def _corbel_on_field_update(
        self,
        field: Field,
        value: Any,
        old_value: Any,
    ) -> None:
        """
        Called whenever a field's value is updated.

        :param field:
            The dataclass field being updated.
        :param value:
            The new value assigned to the field.
        :param old_value:
            The previous value of the field.
        """


__all__ = ("HooksProtocol",)

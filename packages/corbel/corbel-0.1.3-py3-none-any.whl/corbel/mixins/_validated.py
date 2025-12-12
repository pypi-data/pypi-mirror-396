from __future__ import annotations

from typing import TYPE_CHECKING

from ._corbel import Corbel
from ..errors import ValidationError

if TYPE_CHECKING:
    from dataclasses import Field
    from typing import Any


class Validated(Corbel):
    """
    Mixin for dataclasses providing automatic field validation.

    Uses validator functions defined in field metadata under the key 'validator'.
    Fields may allow `None` if 'allow_none' is True. Raises `ValidationError`
    on validation failures.
    """

    def __post_init__(
        self,
    ):
        """
        Validate all fields after dataclass initialization.

        Iterates through all fields and validates their values using the
        associated validator from metadata. Skips validation for fields
        with `None` values if 'allow_none' is True.

        :raises ValidationError:
            If a field fails validation or the validator raises an exception.
        """
        super().__post_init__()

        for field in self.corbel_fields:
            value = getattr(self, field.name)
            self._validate_field(field, value)

    def _corbel_on_field_update(
        self,
        field: Field,
        value: Any,
        old_value: Any,
    ) -> None:
        """
        Validate a field whenever its value is updated.

        :param field:
            The dataclass field being updated.
        :param value:
            The new value assigned to the field.
        :param old_value:
            The previous value of the field.
        """
        super()._corbel_on_field_update(field, value, old_value)
        self._validate_field(field, value)

    def _corbel_on_validation(
        self,
        field: Field,
        value: Any,
        *,
        error: tuple[str, Exception | None] | None = None,
    ) -> None:
        """
        Hook called when a validation error occurs.

        Raises `ValidationError` with the provided message and field info.

        :param field:
            The dataclass field being validated.
        :param value:
            The value that failed validation.
        :param error:
            Tuple containing error message and optional exception.
        """
        super()._corbel_on_validation(field, value, error=error)

        if error:
            message, exception = error

            raise ValidationError(
                message=message,
                field=field,
                value=value,
                error=exception,
            )

    def _validate_field(
        self,
        field: Field,
        value: Any,
    ) -> None:
        """
        Perform validation on a single field.

        Skips validation if `_corbel_validation` is False.
        Uses the validator from field metadata. If `allow_none` is True
        and the value is None, validation is skipped.

        :param field:
            The dataclass field to validate.
        :param value:
            The value to validate.
        """
        if not self._corbel_validation:
            return

        error: tuple[str, Exception | None] | None = None
        metadata = self.corbel_metadata(field)
        allow_none = metadata.get("allow_none", False)
        validator = metadata.get("validator", None)

        try:
            if (value is None and allow_none) or validator is None:
                return

            try:
                is_validated = validator(value)

                if not is_validated:
                    error = (f"Validation failed for field '{field.name}'", None)
            except Exception as e:
                error = (f"Validation failed for field '{field.name}'", e)
        finally:
            self._corbel_on_validation(field, value, error=error)


__all__ = ("Validated",)

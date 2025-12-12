from __future__ import annotations

from typing import TYPE_CHECKING

from ._base import BaseMixin

if TYPE_CHECKING:
    from dataclasses import Field
    from typing import Any


class HooksMixin(BaseMixin):
    """
    Mixin providing automatic hook invocation for dataclass-like objects.

    Triggers `_on_field_update` when attributes are updated after initialization.
    """

    __corbel_initialized: bool = False

    def __post_init__(
        self,
    ) -> None:
        """
        Marks the instance as initialized after dataclass __init__.
        """
        self.__corbel_initialized = True

    def __setattr__(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Override `__setattr__` to trigger hooks on field updates.

        :param key:
            Name of the attribute being set.
        :param value:
            New value to assign to the attribute.
        """
        old_value = getattr(self, key, None)

        super().__setattr__(key, value)

        if getattr(self, "_corbel_initialized"):
            field: Field | None = getattr(self, "__dataclass_fields__", {}).get(
                key, None
            )

            if field is not None and hasattr(self, "_corbel_on_field_update"):
                self._corbel_on_field_update(field, value, old_value)

    def _corbel_on_validation(
        self,
        field: Field,
        value: Any,
        *,
        error: tuple[str, Exception | None] | None = None,
    ) -> None:
        """
        Hook called after a field has been validated.

        Override this method in subclasses to handle validation events.

        :param field:
            The dataclass field being validated.
        :param value:
            The value that was validated.
        :param error:
            Optional tuple containing a validation error message and the
            exception that was raised, if any.
        """
        pass

    def _corbel_on_field_update(
        self,
        field: Field,
        value: Any,
        old_value: Any,
    ) -> None:
        """
        Hook called after a field has been updated.

        Override this method in subclasses to handle field update events.

        :param field:
            The dataclass field being updated.
        :param value:
            The new value assigned to the field.
        :param old_value:
            The previous value of the field.
        """
        pass

    @property
    def _corbel_initialized(
        self,
    ) -> bool:
        """
        Indicates whether the dataclass instance has been fully initialized.

        :return:
            True if __post_init__ has run.
        """
        return self.__corbel_initialized


__all__ = ("HooksMixin",)

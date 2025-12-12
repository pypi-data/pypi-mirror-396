from __future__ import annotations

from typing import TypedDict, TYPE_CHECKING

from corbel.protocols import DeserializerProtocol, SerializerProtocol, ValidatorProtocol

if TYPE_CHECKING:
    from typing import Any, Callable


class CorbelPropertyMetadata(TypedDict, total=False):
    json: dict[str, Any]
    ignore: bool
    allow_none: bool
    validator: ValidatorProtocol | None
    serializer: SerializerProtocol | None
    deserializer: DeserializerProtocol | None


class CorbelProperty(property):
    """
    Custom property that stores Corbel-specific metadata.

    Supports JSON serialization, validation, and custom (de)serializers.
    Fully compatible with @x.setter and @x.deleter.
    """

    def __init__(
        self,
        fget: Callable[..., Any] | None,
        fset: Callable[..., Any] | None = None,
        fdel: Callable[..., Any] | None = None,
        doc: str | None = None,
        *,
        json: dict[str, Any] | None = None,
        ignore: bool = False,
        allow_none: bool = False,
        validator: ValidatorProtocol | None = None,
        serializer: SerializerProtocol | None = None,
        deserializer: DeserializerProtocol | None = None,
    ):
        """
        Initialize a CorbelProperty with optional metadata.

        :param fget:
            The getter function (cannot be None).
        :param fset:
            Optional setter function.
        :param fdel:
            Optional deleter function.
        :param doc:
            Optional docstring for the property.
        :param json:
            Optional dictionary for JSON serialization metadata.
        :param ignore:
            If True, field is ignored during serialization/deserialization.
        :param allow_none:
            If True, allows the field value to be None without validation error.
        :param validator:
            Optional callable used for validating the property value.
        :param serializer:
            Optional callable used to serialize the property value.
        :param deserializer:
            Optional callable used to deserialize the property value.
        """
        if fget is None:
            raise TypeError("fget cannot be None")

        super().__init__(fget, fset, fdel, doc)

        self.__corbel__: CorbelPropertyMetadata = {
            "json": json if json else {},
            "ignore": ignore,
            "allow_none": allow_none,
            "validator": validator,
            "serializer": serializer,
            "deserializer": deserializer,
        }

    def setter(
        self,
        fset: Callable[..., Any],
    ) -> CorbelProperty:
        """
        Return a new CorbelProperty with an updated setter.

        :param fset:
            The setter function to attach to the property.
        :return:
            A new CorbelProperty instance with the updated setter and same metadata.
        """
        prop = super().setter(fset)
        return CorbelProperty(
            prop.fget,
            prop.fset,
            prop.fdel,
            prop.__doc__,
            **self.__corbel__,
        )

    def deleter(
        self,
        fdel: Callable[..., Any],
    ) -> CorbelProperty:
        """
        Return a new CorbelProperty with an updated deleter.

        :param fdel:
            The deleter function to attach to the property.
        :return:
            A new CorbelProperty instance with the updated deleter and same metadata.
        """
        prop = super().deleter(fdel)
        return CorbelProperty(
            prop.fget,
            prop.fset,
            prop.fdel,
            prop.__doc__,
            **self.__corbel__,
        )


__all__ = ("CorbelProperty",)

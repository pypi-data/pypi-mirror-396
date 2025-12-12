from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from ._corbel import Corbel
from .._utils import to_dict, to_json, from_dict, from_json
from ..enums import Include

if TYPE_CHECKING:
    from json import JSONEncoder, JSONDecoder
    from typing import Any, Callable, Type

    from ..types import DictFactory, ListFactory, MutableDict, TCorbelDataclass


class Serializable(Corbel):
    """
    Mixin for dataclasses providing dictionary and JSON serialization/deserialization.

    Provides methods to convert instances to/from dicts and JSON strings, with
    support for nested dataclasses and custom field-level serializers/deserializers.

    ClassVars:
      __json_wrapper__ : str | None
          Optional default JSON wrapper key for serialized output.
      __inclusion__ : Include | None
          Default inclusion rule for fields (`ALWAYS`, `NON_NONE`, `NON_EMPTY`,
          `NON_DEFAULT`).
    """

    __json_wrapper__: ClassVar[str | None] = None
    __inclusion__: ClassVar[Include | None] = Include.ALWAYS

    @classmethod
    def from_dict(
        cls: type[TCorbelDataclass],
        data: dict,
    ) -> TCorbelDataclass:
        """
        Create an instance of the class from a dictionary.

        Fields marked with `corbel.ignore=True` are skipped. Respects type hints
        and nested dataclasses.

        :param data:
            Dictionary containing field values.
        :return:
            Instance populated from the dictionary.
        """
        return from_dict(cls, data)

    @classmethod
    def from_json(
        cls: type[TCorbelDataclass],
        s: str | bytes | bytearray,
        *,
        wrapper: str | None = None,
        json_cls: Type[JSONDecoder] | None = None,
        object_hook: Callable[[dict[Any, Any]], Any] | None = None,
        parse_float: Callable[[str], Any] | None = None,
        parse_int: Callable[[str], Any] | None = None,
        parse_constant: Callable[[str], Any] | None = None,
        object_hook_pairs: Callable[[list[tuple[Any, Any]]], Any] | None = None,
    ) -> TCorbelDataclass:
        """
        Create an instance from a JSON string, bytes, or bytearray.

        Supports wrapper, nested dataclasses, and standard JSON decoder options.

        :param s:
            JSON string, bytes, or bytearray.
        :param wrapper:
            Optional JSON wrapper key. Defaults to `__json_wrapper__`.
        :param json_cls:
            Optional JSON decoder class.
        :param object_hook:
            Optional callable for decoding objects.
        :param parse_float:
            Optional callable to parse floats.
        :param parse_int:
            Optional callable to parse integers.
        :param parse_constant:
            Optional callable to handle NaN/Infinity.
        :param object_hook_pairs:
            Optional callable for decoding key-value pairs.
        :return:
            Instance populated from the JSON data.
        """
        wrapper = wrapper or getattr(cls, "__json_wrapper__")
        return from_json(
            cls,
            s,
            wrapper=wrapper,
            json_cls=json_cls,
            object_hook=object_hook,
            parse_float=parse_float,
            parse_int=parse_int,
            parse_constant=parse_constant,
            object_hook_pairs=object_hook_pairs,
        )

    def to_dict(
        self,
        *,
        include: Include | None = None,
        include_properties: bool = True,
        include_private: bool = False,
        dict_factory: DictFactory = dict,
        list_factory: ListFactory = list,
    ) -> MutableDict:
        """
        Serialize the instance to a dictionary.

        Uses class-level inclusion rule `__inclusion__` by default, but can be
        overridden per-call. Nested dataclasses are fully serialized.

        :param include:
            Optional inclusion rule for fields.
        :param include_properties:
            Include properties in the output if True.
        :param include_private:
            Include private attributes if True.
        :param dict_factory:
            Callable to construct the resulting dictionary.
        :param list_factory:
            Callable to construct lists in the dictionary.
        :return:
            Dictionary representation of the instance.
        """
        if include is None:
            include = getattr(type(self), "__inclusion__", Include.ALWAYS)

        return to_dict(
            self,
            include,
            include_properties=include_properties,
            include_private=include_private,
            dict_factory=dict_factory,
            list_factory=list_factory,
        )

    def to_json(
        self,
        *,
        wrapper: str | None = None,
        include: Include | None = None,
        include_properties: bool = True,
        include_private: bool = False,
        dict_factory: DictFactory = dict,
        list_factory: ListFactory = list,
        skip_keys: bool = False,
        ensure_ascii: bool = True,
        check_circular: bool = True,
        allow_nan: bool = True,
        json_cls: Type[JSONEncoder] | None = None,
        indent: int | None = None,
        separators: tuple[str, str] | None = None,
        default: Callable[[Any], Any] | None = None,
        sort_keys: bool = False,
        **kwargs: Any,
    ) -> str:
        """
        Serialize the instance to a JSON string.

        Allows per-call control of wrapper and inclusion. Respects nested dataclasses
        and supports additional JSON encoder arguments.

        :param wrapper:
            Optional JSON wrapper key. Defaults to `__json_wrapper__`.
        :param include:
            Optional field inclusion rule. Defaults to `__inclusion__`.
        :param include_properties:
            Include properties in the output if True.
        :param include_private:
            Include private attributes if True.
        :param dict_factory:
            Callable to construct the resulting dictionary.
        :param list_factory:
            Callable to construct lists in the dictionary.
        :param skip_keys:
            Skip keys that cannot be serialized.
        :param ensure_ascii:
            Escape non-ASCII characters if True.
        :param check_circular:
            Check for circular references.
        :param allow_nan:
            Allow NaN, Infinity, -Infinity.
        :param json_cls:
            Optional JSON encoder class.
        :param indent:
            Optional indentation for JSON output.
        :param separators:
            Optional separators for JSON output.
        :param default:
            Callable for objects not serializable by default.
        :param sort_keys:
            Sort dictionary keys if True.
        :param kwargs:
            Additional keyword arguments for JSON encoder.
        :return:
            JSON string representation of the instance.
        """
        wrapper = wrapper or getattr(type(self), "__json_wrapper__")

        if include is None:
            include = getattr(type(self), "__inclusion__", Include.ALWAYS)

        return to_json(
            self,
            include,
            wrapper=wrapper,
            include_properties=include_properties,
            include_private=include_private,
            dict_factory=dict_factory,
            list_factory=list_factory,
            skip_keys=skip_keys,
            ensure_ascii=ensure_ascii,
            check_circular=check_circular,
            allow_nan=allow_nan,
            json_cls=json_cls,
            indent=indent,
            separators=separators,
            default=default,
            sort_keys=sort_keys,
            **kwargs,
        )


__all__ = ("Serializable",)

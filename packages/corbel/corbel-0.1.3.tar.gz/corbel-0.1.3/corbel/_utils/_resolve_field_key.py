from __future__ import annotations

from typing import TYPE_CHECKING

from ._corbel_metadata import corbel_metadata

if TYPE_CHECKING:
    from dataclasses import Field
    from typing import Any


def resolve_field_key(
    field: Field,
    data: dict[str, Any],
) -> str:
    """
    Resolve the appropriate dictionary key for a dataclass field.

    Checks the field's JSON metadata for a specific key or any defined aliases.
    Returns the first matching key found in the data, or defaults to the
    field's name if no matches are found.

    :param field:
        The dataclass field for which to resolve the key.
    :param data:
        Dictionary containing data being deserialized.
    :return:
        The key from the dictionary to use for this field.
    :rtype: str
    """
    metadata = corbel_metadata(field, "json", {})
    key: str | None = metadata.get("key")

    if key and key in data:
        return key

    aliases = metadata.get("aliases", [])
    if isinstance(aliases, str):
        aliases = [aliases]

    for alias in aliases:
        if alias in data:
            return alias

    return field.name


__all__ = ("resolve_field_key",)

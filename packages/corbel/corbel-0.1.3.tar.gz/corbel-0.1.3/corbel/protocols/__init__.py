from __future__ import annotations

from ._dataclass import CorbelDataclass
from ._deserializer import DeserializerProtocol
from ._hooks import HooksProtocol
from ._member import MemberCaptureProtocol
from ._serializer import SerializerProtocol
from ._validator import ValidatorProtocol


__all__ = (
    "DeserializerProtocol",
    "HooksProtocol",
    "MemberCaptureProtocol",
    "SerializerProtocol",
    "ValidatorProtocol",
    "CorbelDataclass",
)

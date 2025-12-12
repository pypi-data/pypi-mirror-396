from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ARClientRole(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AR_CLIENT_ROLE_UNSPECIFIED: _ClassVar[ARClientRole]
    AR_CLIENT_ROLE_MAIN: _ClassVar[ARClientRole]
    AR_CLIENT_ROLE_SPECTATOR: _ClassVar[ARClientRole]
AR_CLIENT_ROLE_UNSPECIFIED: ARClientRole
AR_CLIENT_ROLE_MAIN: ARClientRole
AR_CLIENT_ROLE_SPECTATOR: ARClientRole

class ARClientMessage(_message.Message):
    __slots__ = ("id", "role", "operator_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    OPERATOR_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    role: ARClientRole
    operator_id: str
    def __init__(self, id: _Optional[str] = ..., role: _Optional[_Union[ARClientRole, str]] = ..., operator_id: _Optional[str] = ...) -> None: ...

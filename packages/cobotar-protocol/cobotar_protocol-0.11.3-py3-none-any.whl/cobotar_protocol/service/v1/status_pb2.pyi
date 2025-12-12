from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STATUS_UNSPECIFIED: _ClassVar[Status]
    STATUS_OFFLINE: _ClassVar[Status]
    STATUS_ONLINE: _ClassVar[Status]
STATUS_UNSPECIFIED: Status
STATUS_OFFLINE: Status
STATUS_ONLINE: Status

class ServiceStatus(_message.Message):
    __slots__ = ("id", "name", "description", "type", "ip", "status")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    IP_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    type: str
    ip: str
    status: Status
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., type: _Optional[str] = ..., ip: _Optional[str] = ..., status: _Optional[_Union[Status, str]] = ...) -> None: ...

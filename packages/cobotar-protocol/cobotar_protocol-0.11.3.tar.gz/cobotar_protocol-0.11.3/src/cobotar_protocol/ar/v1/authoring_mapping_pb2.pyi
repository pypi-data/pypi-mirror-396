from ar.v1 import mapping_pb2 as _mapping_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MappingNewMessage(_message.Message):
    __slots__ = ("name", "icon", "description")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ICON_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    name: str
    icon: str
    description: str
    def __init__(self, name: _Optional[str] = ..., icon: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class MappingUpdateMessage(_message.Message):
    __slots__ = ("id", "name", "icon", "description", "environment_ids", "ar_config_priorities")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ICON_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_IDS_FIELD_NUMBER: _ClassVar[int]
    AR_CONFIG_PRIORITIES_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    icon: str
    description: str
    environment_ids: _containers.RepeatedScalarFieldContainer[str]
    ar_config_priorities: _containers.RepeatedCompositeFieldContainer[_mapping_pb2.ARPriority]
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., icon: _Optional[str] = ..., description: _Optional[str] = ..., environment_ids: _Optional[_Iterable[str]] = ..., ar_config_priorities: _Optional[_Iterable[_Union[_mapping_pb2.ARPriority, _Mapping]]] = ...) -> None: ...

class MappingDeleteMessage(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

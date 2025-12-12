from ar.v1 import environment_pb2 as _environment_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EnvironmentNewMessage(_message.Message):
    __slots__ = ("name", "icon", "description", "type")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ICON_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    name: str
    icon: str
    description: str
    type: _environment_pb2.EnvironmentType
    def __init__(self, name: _Optional[str] = ..., icon: _Optional[str] = ..., description: _Optional[str] = ..., type: _Optional[_Union[_environment_pb2.EnvironmentType, str]] = ...) -> None: ...

class EnvironmentUpdateMessage(_message.Message):
    __slots__ = ("id", "name", "icon", "description", "type", "markers", "agents", "parts", "tools")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ICON_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    MARKERS_FIELD_NUMBER: _ClassVar[int]
    AGENTS_FIELD_NUMBER: _ClassVar[int]
    PARTS_FIELD_NUMBER: _ClassVar[int]
    TOOLS_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    icon: str
    description: str
    type: _environment_pb2.EnvironmentType
    markers: _containers.RepeatedCompositeFieldContainer[_environment_pb2.MarkerLocation]
    agents: _containers.RepeatedCompositeFieldContainer[_environment_pb2.AgentLocation]
    parts: _containers.RepeatedCompositeFieldContainer[_environment_pb2.PartLocation]
    tools: _containers.RepeatedCompositeFieldContainer[_environment_pb2.ToolLocation]
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., icon: _Optional[str] = ..., description: _Optional[str] = ..., type: _Optional[_Union[_environment_pb2.EnvironmentType, str]] = ..., markers: _Optional[_Iterable[_Union[_environment_pb2.MarkerLocation, _Mapping]]] = ..., agents: _Optional[_Iterable[_Union[_environment_pb2.AgentLocation, _Mapping]]] = ..., parts: _Optional[_Iterable[_Union[_environment_pb2.PartLocation, _Mapping]]] = ..., tools: _Optional[_Iterable[_Union[_environment_pb2.ToolLocation, _Mapping]]] = ...) -> None: ...

class EnvironmentDeleteMessage(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

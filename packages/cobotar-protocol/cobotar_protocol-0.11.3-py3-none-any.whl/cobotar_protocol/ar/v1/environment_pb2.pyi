from ar.v1 import property_pb2 as _property_pb2
from geometry.v1 import pose_pb2 as _pose_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EnvironmentType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ENVIRONMENT_TYPE_UNSPECIFIED: _ClassVar[EnvironmentType]
    ENVIRONMENT_TYPE_STORAGE: _ClassVar[EnvironmentType]
    ENVIRONMENT_TYPE_MANUAL_STATION: _ClassVar[EnvironmentType]
    ENVIRONMENT_TYPE_AUTOMATIC_STATION: _ClassVar[EnvironmentType]
    ENVIRONMENT_TYPE_HYBRID_STATION: _ClassVar[EnvironmentType]
    ENVIRONMENT_TYPE_MANUAL_LINE: _ClassVar[EnvironmentType]
    ENVIRONMENT_TYPE_AUTOMATIC_LINE: _ClassVar[EnvironmentType]
    ENVIRONMENT_TYPE_HYBRID_LINE: _ClassVar[EnvironmentType]
ENVIRONMENT_TYPE_UNSPECIFIED: EnvironmentType
ENVIRONMENT_TYPE_STORAGE: EnvironmentType
ENVIRONMENT_TYPE_MANUAL_STATION: EnvironmentType
ENVIRONMENT_TYPE_AUTOMATIC_STATION: EnvironmentType
ENVIRONMENT_TYPE_HYBRID_STATION: EnvironmentType
ENVIRONMENT_TYPE_MANUAL_LINE: EnvironmentType
ENVIRONMENT_TYPE_AUTOMATIC_LINE: EnvironmentType
ENVIRONMENT_TYPE_HYBRID_LINE: EnvironmentType

class MarkerLocation(_message.Message):
    __slots__ = ("id", "location")
    ID_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    id: str
    location: _pose_pb2.LocalizedPose
    def __init__(self, id: _Optional[str] = ..., location: _Optional[_Union[_pose_pb2.LocalizedPose, _Mapping]] = ...) -> None: ...

class AgentLocation(_message.Message):
    __slots__ = ("id", "location")
    ID_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    id: str
    location: _pose_pb2.LocalizedPose
    def __init__(self, id: _Optional[str] = ..., location: _Optional[_Union[_pose_pb2.LocalizedPose, _Mapping]] = ...) -> None: ...

class PartLocation(_message.Message):
    __slots__ = ("id", "location")
    ID_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    id: str
    location: _pose_pb2.LocalizedPose
    def __init__(self, id: _Optional[str] = ..., location: _Optional[_Union[_pose_pb2.LocalizedPose, _Mapping]] = ...) -> None: ...

class ToolLocation(_message.Message):
    __slots__ = ("id", "location")
    ID_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    id: str
    location: _pose_pb2.LocalizedPose
    def __init__(self, id: _Optional[str] = ..., location: _Optional[_Union[_pose_pb2.LocalizedPose, _Mapping]] = ...) -> None: ...

class EnvironmentMessage(_message.Message):
    __slots__ = ("id", "name", "icon", "description", "type", "markers", "agents", "parts", "tools", "properties")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ICON_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    MARKERS_FIELD_NUMBER: _ClassVar[int]
    AGENTS_FIELD_NUMBER: _ClassVar[int]
    PARTS_FIELD_NUMBER: _ClassVar[int]
    TOOLS_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    icon: str
    description: str
    type: EnvironmentType
    markers: _containers.RepeatedCompositeFieldContainer[MarkerLocation]
    agents: _containers.RepeatedCompositeFieldContainer[AgentLocation]
    parts: _containers.RepeatedCompositeFieldContainer[PartLocation]
    tools: _containers.RepeatedCompositeFieldContainer[ToolLocation]
    properties: _containers.RepeatedCompositeFieldContainer[_property_pb2.Property]
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., icon: _Optional[str] = ..., description: _Optional[str] = ..., type: _Optional[_Union[EnvironmentType, str]] = ..., markers: _Optional[_Iterable[_Union[MarkerLocation, _Mapping]]] = ..., agents: _Optional[_Iterable[_Union[AgentLocation, _Mapping]]] = ..., parts: _Optional[_Iterable[_Union[PartLocation, _Mapping]]] = ..., tools: _Optional[_Iterable[_Union[ToolLocation, _Mapping]]] = ..., properties: _Optional[_Iterable[_Union[_property_pb2.Property, _Mapping]]] = ...) -> None: ...

class EnvironmentsMessage(_message.Message):
    __slots__ = ("environments",)
    ENVIRONMENTS_FIELD_NUMBER: _ClassVar[int]
    environments: _containers.RepeatedCompositeFieldContainer[EnvironmentMessage]
    def __init__(self, environments: _Optional[_Iterable[_Union[EnvironmentMessage, _Mapping]]] = ...) -> None: ...

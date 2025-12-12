from ar.v1 import property_pb2 as _property_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ActionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ACTION_TYPE_UNSPECIFIED: _ClassVar[ActionType]
    ACTION_TYPE_TASK_COMPLETE: _ClassVar[ActionType]
    ACTION_TYPE_TASK_UNDO: _ClassVar[ActionType]
    ACTION_TYPE_TASK_ASSIGN: _ClassVar[ActionType]
    ACTION_TYPE_TASK_HIGHLIGHT: _ClassVar[ActionType]
    ACTION_TYPE_TASK_HELP: _ClassVar[ActionType]
    ACTION_TYPE_ROBOT_PLAY_PAUSE: _ClassVar[ActionType]
    ACTION_TYPE_ROBOT_ACKNOWLEDGE: _ClassVar[ActionType]
ACTION_TYPE_UNSPECIFIED: ActionType
ACTION_TYPE_TASK_COMPLETE: ActionType
ACTION_TYPE_TASK_UNDO: ActionType
ACTION_TYPE_TASK_ASSIGN: ActionType
ACTION_TYPE_TASK_HIGHLIGHT: ActionType
ACTION_TYPE_TASK_HELP: ActionType
ACTION_TYPE_ROBOT_PLAY_PAUSE: ActionType
ACTION_TYPE_ROBOT_ACKNOWLEDGE: ActionType

class ActionMessage(_message.Message):
    __slots__ = ("id", "name", "icon", "description", "type", "properties", "output_properties")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ICON_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    icon: str
    description: str
    type: ActionType
    properties: _containers.RepeatedCompositeFieldContainer[_property_pb2.Property]
    output_properties: _containers.RepeatedCompositeFieldContainer[_property_pb2.Property]
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., icon: _Optional[str] = ..., description: _Optional[str] = ..., type: _Optional[_Union[ActionType, str]] = ..., properties: _Optional[_Iterable[_Union[_property_pb2.Property, _Mapping]]] = ..., output_properties: _Optional[_Iterable[_Union[_property_pb2.Property, _Mapping]]] = ...) -> None: ...

from ar.v1 import property_pb2 as _property_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FeedbackType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FEEDBACK_TYPE_UNSPECIFIED: _ClassVar[FeedbackType]
    FEEDBACK_TYPE_TASK_HIGHLIGHT: _ClassVar[FeedbackType]
    FEEDBACK_TYPE_TASK_PART_HIGHLIGHT: _ClassVar[FeedbackType]
    FEEDBACK_TYPE_TASK_TOOL_HIGHLIGHT: _ClassVar[FeedbackType]
    FEEDBACK_TYPE_TASK_OVERVIEW: _ClassVar[FeedbackType]
    FEEDBACK_TYPE_ROBOT_PATH: _ClassVar[FeedbackType]
    FEEDBACK_TYPE_ROBOT_SILHOUETTE: _ClassVar[FeedbackType]
    FEEDBACK_TYPE_ROBOT_WAYPOINTS: _ClassVar[FeedbackType]
    FEEDBACK_TYPE_ROBOT_STATUS: _ClassVar[FeedbackType]
    FEEDBACK_TYPE_ROBOT_LIGHT: _ClassVar[FeedbackType]
    FEEDBACK_TYPE_MESSAGE: _ClassVar[FeedbackType]
    FEEDBACK_TYPE_ICON: _ClassVar[FeedbackType]
    FEEDBACK_TYPE_ZONE: _ClassVar[FeedbackType]
    FEEDBACK_TYPE_PLAY_SOUND: _ClassVar[FeedbackType]
    FEEDBACK_TYPE_RULER: _ClassVar[FeedbackType]
FEEDBACK_TYPE_UNSPECIFIED: FeedbackType
FEEDBACK_TYPE_TASK_HIGHLIGHT: FeedbackType
FEEDBACK_TYPE_TASK_PART_HIGHLIGHT: FeedbackType
FEEDBACK_TYPE_TASK_TOOL_HIGHLIGHT: FeedbackType
FEEDBACK_TYPE_TASK_OVERVIEW: FeedbackType
FEEDBACK_TYPE_ROBOT_PATH: FeedbackType
FEEDBACK_TYPE_ROBOT_SILHOUETTE: FeedbackType
FEEDBACK_TYPE_ROBOT_WAYPOINTS: FeedbackType
FEEDBACK_TYPE_ROBOT_STATUS: FeedbackType
FEEDBACK_TYPE_ROBOT_LIGHT: FeedbackType
FEEDBACK_TYPE_MESSAGE: FeedbackType
FEEDBACK_TYPE_ICON: FeedbackType
FEEDBACK_TYPE_ZONE: FeedbackType
FEEDBACK_TYPE_PLAY_SOUND: FeedbackType
FEEDBACK_TYPE_RULER: FeedbackType

class FeedbackMessage(_message.Message):
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
    type: FeedbackType
    properties: _containers.RepeatedCompositeFieldContainer[_property_pb2.Property]
    output_properties: _containers.RepeatedCompositeFieldContainer[_property_pb2.Property]
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., icon: _Optional[str] = ..., description: _Optional[str] = ..., type: _Optional[_Union[FeedbackType, str]] = ..., properties: _Optional[_Iterable[_Union[_property_pb2.Property, _Mapping]]] = ..., output_properties: _Optional[_Iterable[_Union[_property_pb2.Property, _Mapping]]] = ...) -> None: ...

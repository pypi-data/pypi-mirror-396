from ar.v1 import events_pb2 as _events_pb2
from ar.v1 import feedback_pb2 as _feedback_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FeedbackInfoMessage(_message.Message):
    __slots__ = ("name", "icon", "description", "type", "group", "require_agent", "require_frame", "required_events", "optional_events", "disabled")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ICON_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    GROUP_FIELD_NUMBER: _ClassVar[int]
    REQUIRE_AGENT_FIELD_NUMBER: _ClassVar[int]
    REQUIRE_FRAME_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_EVENTS_FIELD_NUMBER: _ClassVar[int]
    OPTIONAL_EVENTS_FIELD_NUMBER: _ClassVar[int]
    DISABLED_FIELD_NUMBER: _ClassVar[int]
    name: str
    icon: str
    description: str
    type: _feedback_pb2.FeedbackType
    group: str
    require_agent: bool
    require_frame: bool
    required_events: _containers.RepeatedScalarFieldContainer[_events_pb2.EventType]
    optional_events: _containers.RepeatedScalarFieldContainer[_events_pb2.EventType]
    disabled: bool
    def __init__(self, name: _Optional[str] = ..., icon: _Optional[str] = ..., description: _Optional[str] = ..., type: _Optional[_Union[_feedback_pb2.FeedbackType, str]] = ..., group: _Optional[str] = ..., require_agent: bool = ..., require_frame: bool = ..., required_events: _Optional[_Iterable[_Union[_events_pb2.EventType, str]]] = ..., optional_events: _Optional[_Iterable[_Union[_events_pb2.EventType, str]]] = ..., disabled: bool = ...) -> None: ...

class FeedbackInfosMessage(_message.Message):
    __slots__ = ("feedback_infos",)
    FEEDBACK_INFOS_FIELD_NUMBER: _ClassVar[int]
    feedback_infos: _containers.RepeatedCompositeFieldContainer[FeedbackInfoMessage]
    def __init__(self, feedback_infos: _Optional[_Iterable[_Union[FeedbackInfoMessage, _Mapping]]] = ...) -> None: ...

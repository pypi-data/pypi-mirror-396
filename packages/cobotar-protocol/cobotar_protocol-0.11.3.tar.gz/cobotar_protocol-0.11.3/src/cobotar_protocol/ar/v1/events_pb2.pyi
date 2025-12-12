from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EventType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EVENT_TYPE_UNSPECIFIED: _ClassVar[EventType]
    EVENT_TYPE_TASK_COMPLETE: _ClassVar[EventType]
    EVENT_TYPE_TASK_UNDO: _ClassVar[EventType]
    EVENT_TYPE_TASK_ASSIGN: _ClassVar[EventType]
    EVENT_TYPE_TASK_HIGHLIGHT: _ClassVar[EventType]
    EVENT_TYPE_TASK_HELP: _ClassVar[EventType]
    EVENT_TYPE_ROBOT_TCP: _ClassVar[EventType]
    EVENT_TYPE_ROBOT_JOINT_ANGLES: _ClassVar[EventType]
    EVENT_TYPE_ROBOT_FORCE_TORQUE: _ClassVar[EventType]
    EVENT_TYPE_ROBOT_STATE: _ClassVar[EventType]
    EVENT_TYPE_ROBOT_PATH: _ClassVar[EventType]
    EVENT_TYPE_ROBOT_WAYPOINTS: _ClassVar[EventType]
EVENT_TYPE_UNSPECIFIED: EventType
EVENT_TYPE_TASK_COMPLETE: EventType
EVENT_TYPE_TASK_UNDO: EventType
EVENT_TYPE_TASK_ASSIGN: EventType
EVENT_TYPE_TASK_HIGHLIGHT: EventType
EVENT_TYPE_TASK_HELP: EventType
EVENT_TYPE_ROBOT_TCP: EventType
EVENT_TYPE_ROBOT_JOINT_ANGLES: EventType
EVENT_TYPE_ROBOT_FORCE_TORQUE: EventType
EVENT_TYPE_ROBOT_STATE: EventType
EVENT_TYPE_ROBOT_PATH: EventType
EVENT_TYPE_ROBOT_WAYPOINTS: EventType

class SupportedEventsMessage(_message.Message):
    __slots__ = ("events",)
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    events: _containers.RepeatedScalarFieldContainer[EventType]
    def __init__(self, events: _Optional[_Iterable[_Union[EventType, str]]] = ...) -> None: ...

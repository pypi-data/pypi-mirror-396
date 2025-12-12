from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class JointStateMessage(_message.Message):
    __slots__ = ("robot_id", "live", "position", "velocity")
    ROBOT_ID_FIELD_NUMBER: _ClassVar[int]
    LIVE_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    VELOCITY_FIELD_NUMBER: _ClassVar[int]
    robot_id: str
    live: bool
    position: _containers.RepeatedScalarFieldContainer[float]
    velocity: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, robot_id: _Optional[str] = ..., live: bool = ..., position: _Optional[_Iterable[float]] = ..., velocity: _Optional[_Iterable[float]] = ...) -> None: ...

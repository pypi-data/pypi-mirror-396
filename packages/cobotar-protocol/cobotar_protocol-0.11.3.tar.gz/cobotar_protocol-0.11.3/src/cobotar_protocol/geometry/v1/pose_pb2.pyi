import datetime

from geometry.v1 import point_pb2 as _point_pb2
from geometry.v1 import quad_pb2 as _quad_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LocalizedState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LOCALIZED_STATE_UNSPECIFIED: _ClassVar[LocalizedState]
    LOCALIZED_STATE_FOUND: _ClassVar[LocalizedState]
    LOCALIZED_STATE_LOST: _ClassVar[LocalizedState]
    LOCALIZED_STATE_STATIC: _ClassVar[LocalizedState]
    LOCALIZED_STATE_UNKNOWN: _ClassVar[LocalizedState]
LOCALIZED_STATE_UNSPECIFIED: LocalizedState
LOCALIZED_STATE_FOUND: LocalizedState
LOCALIZED_STATE_LOST: LocalizedState
LOCALIZED_STATE_STATIC: LocalizedState
LOCALIZED_STATE_UNKNOWN: LocalizedState

class Pose(_message.Message):
    __slots__ = ("position", "orientation")
    POSITION_FIELD_NUMBER: _ClassVar[int]
    ORIENTATION_FIELD_NUMBER: _ClassVar[int]
    position: _point_pb2.Point
    orientation: _quad_pb2.Quad
    def __init__(self, position: _Optional[_Union[_point_pb2.Point, _Mapping]] = ..., orientation: _Optional[_Union[_quad_pb2.Quad, _Mapping]] = ...) -> None: ...

class LocalizedPose(_message.Message):
    __slots__ = ("pose", "anchor_id", "state", "last_updated")
    POSE_FIELD_NUMBER: _ClassVar[int]
    ANCHOR_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    LAST_UPDATED_FIELD_NUMBER: _ClassVar[int]
    pose: Pose
    anchor_id: str
    state: LocalizedState
    last_updated: _timestamp_pb2.Timestamp
    def __init__(self, pose: _Optional[_Union[Pose, _Mapping]] = ..., anchor_id: _Optional[str] = ..., state: _Optional[_Union[LocalizedState, str]] = ..., last_updated: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

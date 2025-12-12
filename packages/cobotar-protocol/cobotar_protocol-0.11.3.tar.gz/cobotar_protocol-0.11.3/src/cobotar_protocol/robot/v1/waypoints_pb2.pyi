from geometry.v1 import point_pb2 as _point_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class WaypointMessage(_message.Message):
    __slots__ = ("name", "point")
    NAME_FIELD_NUMBER: _ClassVar[int]
    POINT_FIELD_NUMBER: _ClassVar[int]
    name: str
    point: _point_pb2.Point
    def __init__(self, name: _Optional[str] = ..., point: _Optional[_Union[_point_pb2.Point, _Mapping]] = ...) -> None: ...

class WaypointsMessage(_message.Message):
    __slots__ = ("id", "robot_id", "frame_id", "highlight_idx", "waypoints")
    ID_FIELD_NUMBER: _ClassVar[int]
    ROBOT_ID_FIELD_NUMBER: _ClassVar[int]
    FRAME_ID_FIELD_NUMBER: _ClassVar[int]
    HIGHLIGHT_IDX_FIELD_NUMBER: _ClassVar[int]
    WAYPOINTS_FIELD_NUMBER: _ClassVar[int]
    id: str
    robot_id: str
    frame_id: str
    highlight_idx: int
    waypoints: _containers.RepeatedCompositeFieldContainer[WaypointMessage]
    def __init__(self, id: _Optional[str] = ..., robot_id: _Optional[str] = ..., frame_id: _Optional[str] = ..., highlight_idx: _Optional[int] = ..., waypoints: _Optional[_Iterable[_Union[WaypointMessage, _Mapping]]] = ...) -> None: ...

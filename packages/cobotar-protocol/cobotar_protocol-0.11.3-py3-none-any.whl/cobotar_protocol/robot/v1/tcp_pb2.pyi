from geometry.v1 import point_pb2 as _point_pb2
from geometry.v1 import quad_pb2 as _quad_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TcpMessage(_message.Message):
    __slots__ = ("robot_id", "position", "orientation")
    ROBOT_ID_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    ORIENTATION_FIELD_NUMBER: _ClassVar[int]
    robot_id: str
    position: _point_pb2.Point
    orientation: _quad_pb2.Quad
    def __init__(self, robot_id: _Optional[str] = ..., position: _Optional[_Union[_point_pb2.Point, _Mapping]] = ..., orientation: _Optional[_Union[_quad_pb2.Quad, _Mapping]] = ...) -> None: ...

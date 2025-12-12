from geometry.v1 import point_pb2 as _point_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ZoneMessage(_message.Message):
    __slots__ = ("id", "frame_id", "points")
    ID_FIELD_NUMBER: _ClassVar[int]
    FRAME_ID_FIELD_NUMBER: _ClassVar[int]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    id: str
    frame_id: str
    points: _containers.RepeatedCompositeFieldContainer[_point_pb2.Point]
    def __init__(self, id: _Optional[str] = ..., frame_id: _Optional[str] = ..., points: _Optional[_Iterable[_Union[_point_pb2.Point, _Mapping]]] = ...) -> None: ...

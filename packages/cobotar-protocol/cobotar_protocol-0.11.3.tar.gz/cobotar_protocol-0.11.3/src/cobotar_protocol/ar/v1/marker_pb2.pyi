from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MarkerType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MARKER_TYPE_UNSPECIFIED: _ClassVar[MarkerType]
    MARKER_TYPE_QR_CODE: _ClassVar[MarkerType]
MARKER_TYPE_UNSPECIFIED: MarkerType
MARKER_TYPE_QR_CODE: MarkerType

class MarkerMessage(_message.Message):
    __slots__ = ("id", "name", "description", "marker_text", "type")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    MARKER_TEXT_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    marker_text: str
    type: MarkerType
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., marker_text: _Optional[str] = ..., type: _Optional[_Union[MarkerType, str]] = ...) -> None: ...

class MarkersMessage(_message.Message):
    __slots__ = ("markers",)
    MARKERS_FIELD_NUMBER: _ClassVar[int]
    markers: _containers.RepeatedCompositeFieldContainer[MarkerMessage]
    def __init__(self, markers: _Optional[_Iterable[_Union[MarkerMessage, _Mapping]]] = ...) -> None: ...

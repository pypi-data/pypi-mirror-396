from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class MarkerNewMessage(_message.Message):
    __slots__ = ("name", "description", "marker_text")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    MARKER_TEXT_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    marker_text: str
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., marker_text: _Optional[str] = ...) -> None: ...

class MarkerUpdateMessage(_message.Message):
    __slots__ = ("id", "name", "description", "marker_text")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    MARKER_TEXT_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    marker_text: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., marker_text: _Optional[str] = ...) -> None: ...

class MarkerDeleteMessage(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

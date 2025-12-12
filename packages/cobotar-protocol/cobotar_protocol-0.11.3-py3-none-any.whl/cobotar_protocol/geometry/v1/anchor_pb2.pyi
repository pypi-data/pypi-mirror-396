from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Anchor(_message.Message):
    __slots__ = ("reference", "frame")
    REFERENCE_FIELD_NUMBER: _ClassVar[int]
    FRAME_FIELD_NUMBER: _ClassVar[int]
    reference: str
    frame: str
    def __init__(self, reference: _Optional[str] = ..., frame: _Optional[str] = ...) -> None: ...

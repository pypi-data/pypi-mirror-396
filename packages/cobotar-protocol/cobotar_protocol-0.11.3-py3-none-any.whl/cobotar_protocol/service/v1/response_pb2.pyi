from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Response(_message.Message):
    __slots__ = ("request_id", "success", "message")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    success: bool
    message: str
    def __init__(self, request_id: _Optional[str] = ..., success: bool = ..., message: _Optional[str] = ...) -> None: ...

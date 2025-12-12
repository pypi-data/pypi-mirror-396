from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class SequenceReassignMessage(_message.Message):
    __slots__ = ("request_id", "instance_id", "sequence_id", "assignee")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_ID_FIELD_NUMBER: _ClassVar[int]
    ASSIGNEE_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    instance_id: str
    sequence_id: str
    assignee: str
    def __init__(self, request_id: _Optional[str] = ..., instance_id: _Optional[str] = ..., sequence_id: _Optional[str] = ..., assignee: _Optional[str] = ...) -> None: ...

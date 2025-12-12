from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class SequenceBulkCompleteMessage(_message.Message):
    __slots__ = ("request_id", "instance_id", "sequence_id", "agent_id")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_ID_FIELD_NUMBER: _ClassVar[int]
    AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    instance_id: str
    sequence_id: str
    agent_id: str
    def __init__(self, request_id: _Optional[str] = ..., instance_id: _Optional[str] = ..., sequence_id: _Optional[str] = ..., agent_id: _Optional[str] = ...) -> None: ...

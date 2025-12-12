from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class TaskProgressMessage(_message.Message):
    __slots__ = ("request_id", "instance_id", "task_id", "agent_id", "message", "elapsed_time", "estimated_time_left")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    ELAPSED_TIME_FIELD_NUMBER: _ClassVar[int]
    ESTIMATED_TIME_LEFT_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    instance_id: str
    task_id: str
    agent_id: str
    message: str
    elapsed_time: int
    estimated_time_left: int
    def __init__(self, request_id: _Optional[str] = ..., instance_id: _Optional[str] = ..., task_id: _Optional[str] = ..., agent_id: _Optional[str] = ..., message: _Optional[str] = ..., elapsed_time: _Optional[int] = ..., estimated_time_left: _Optional[int] = ...) -> None: ...

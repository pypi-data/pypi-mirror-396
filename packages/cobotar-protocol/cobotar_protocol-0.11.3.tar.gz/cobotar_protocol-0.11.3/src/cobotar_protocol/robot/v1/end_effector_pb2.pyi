from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class EndEffectorStateMessage(_message.Message):
    __slots__ = ("robot_id", "live", "state")
    ROBOT_ID_FIELD_NUMBER: _ClassVar[int]
    LIVE_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    robot_id: str
    live: bool
    state: str
    def __init__(self, robot_id: _Optional[str] = ..., live: bool = ..., state: _Optional[str] = ...) -> None: ...

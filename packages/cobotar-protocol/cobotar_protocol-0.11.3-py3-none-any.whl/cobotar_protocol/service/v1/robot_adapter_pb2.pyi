from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class RobotAdapterInfoMessage(_message.Message):
    __slots__ = ("robot_id", "robot_type", "identifier")
    ROBOT_ID_FIELD_NUMBER: _ClassVar[int]
    ROBOT_TYPE_FIELD_NUMBER: _ClassVar[int]
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    robot_id: str
    robot_type: str
    identifier: str
    def __init__(self, robot_id: _Optional[str] = ..., robot_type: _Optional[str] = ..., identifier: _Optional[str] = ...) -> None: ...

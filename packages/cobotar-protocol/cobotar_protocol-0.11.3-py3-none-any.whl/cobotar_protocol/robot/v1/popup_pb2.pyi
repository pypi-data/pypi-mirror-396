from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class RobotShowPopupRequest(_message.Message):
    __slots__ = ("request_id", "robot_id", "text")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    ROBOT_ID_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    robot_id: str
    text: str
    def __init__(self, request_id: _Optional[str] = ..., robot_id: _Optional[str] = ..., text: _Optional[str] = ...) -> None: ...

class RobotHidePopupRequest(_message.Message):
    __slots__ = ("request_id", "robot_id")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    ROBOT_ID_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    robot_id: str
    def __init__(self, request_id: _Optional[str] = ..., robot_id: _Optional[str] = ...) -> None: ...

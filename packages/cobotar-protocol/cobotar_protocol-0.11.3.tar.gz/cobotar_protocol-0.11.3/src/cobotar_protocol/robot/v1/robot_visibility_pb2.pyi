from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class RobotVisibilityMessage(_message.Message):
    __slots__ = ("robot_id", "base_visible", "upper_arm_visible", "forearm_visible", "wrist_visible", "end_effector_visible", "tcp_visible")
    ROBOT_ID_FIELD_NUMBER: _ClassVar[int]
    BASE_VISIBLE_FIELD_NUMBER: _ClassVar[int]
    UPPER_ARM_VISIBLE_FIELD_NUMBER: _ClassVar[int]
    FOREARM_VISIBLE_FIELD_NUMBER: _ClassVar[int]
    WRIST_VISIBLE_FIELD_NUMBER: _ClassVar[int]
    END_EFFECTOR_VISIBLE_FIELD_NUMBER: _ClassVar[int]
    TCP_VISIBLE_FIELD_NUMBER: _ClassVar[int]
    robot_id: str
    base_visible: bool
    upper_arm_visible: bool
    forearm_visible: bool
    wrist_visible: bool
    end_effector_visible: bool
    tcp_visible: bool
    def __init__(self, robot_id: _Optional[str] = ..., base_visible: bool = ..., upper_arm_visible: bool = ..., forearm_visible: bool = ..., wrist_visible: bool = ..., end_effector_visible: bool = ..., tcp_visible: bool = ...) -> None: ...

from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RobotState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ROBOT_STATE_UNSPECIFIED: _ClassVar[RobotState]
    ROBOT_STATE_STOPPING: _ClassVar[RobotState]
    ROBOT_STATE_STOPPED: _ClassVar[RobotState]
    ROBOT_STATE_PLAYING: _ClassVar[RobotState]
    ROBOT_STATE_PAUSING: _ClassVar[RobotState]
    ROBOT_STATE_PAUSED: _ClassVar[RobotState]
    ROBOT_STATE_RESUMING: _ClassVar[RobotState]
ROBOT_STATE_UNSPECIFIED: RobotState
ROBOT_STATE_STOPPING: RobotState
ROBOT_STATE_STOPPED: RobotState
ROBOT_STATE_PLAYING: RobotState
ROBOT_STATE_PAUSING: RobotState
ROBOT_STATE_PAUSED: RobotState
ROBOT_STATE_RESUMING: RobotState

class RobotStateMessage(_message.Message):
    __slots__ = ("robot_id", "state_code", "state", "target_speed", "actual_speed")
    ROBOT_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_CODE_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    TARGET_SPEED_FIELD_NUMBER: _ClassVar[int]
    ACTUAL_SPEED_FIELD_NUMBER: _ClassVar[int]
    robot_id: str
    state_code: RobotState
    state: str
    target_speed: float
    actual_speed: float
    def __init__(self, robot_id: _Optional[str] = ..., state_code: _Optional[_Union[RobotState, str]] = ..., state: _Optional[str] = ..., target_speed: _Optional[float] = ..., actual_speed: _Optional[float] = ...) -> None: ...

from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ProgramState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PROGRAM_STATE_UNSPECIFIED: _ClassVar[ProgramState]
    PROGRAM_STATE_PLAY: _ClassVar[ProgramState]
    PROGRAM_STATE_PAUSE: _ClassVar[ProgramState]
    PROGRAM_STATE_STOP: _ClassVar[ProgramState]
PROGRAM_STATE_UNSPECIFIED: ProgramState
PROGRAM_STATE_PLAY: ProgramState
PROGRAM_STATE_PAUSE: ProgramState
PROGRAM_STATE_STOP: ProgramState

class ProgramStateMessage(_message.Message):
    __slots__ = ("robot_id", "state_code", "state", "program_file")
    ROBOT_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_CODE_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    PROGRAM_FILE_FIELD_NUMBER: _ClassVar[int]
    robot_id: str
    state_code: ProgramState
    state: str
    program_file: str
    def __init__(self, robot_id: _Optional[str] = ..., state_code: _Optional[_Union[ProgramState, str]] = ..., state: _Optional[str] = ..., program_file: _Optional[str] = ...) -> None: ...

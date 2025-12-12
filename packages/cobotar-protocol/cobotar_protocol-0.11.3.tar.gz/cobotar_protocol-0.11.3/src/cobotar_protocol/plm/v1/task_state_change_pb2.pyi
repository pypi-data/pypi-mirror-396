from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TaskStateRequest(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TASK_STATE_REQUEST_UNSPECIFIED: _ClassVar[TaskStateRequest]
    TASK_STATE_REQUEST_IN_PROGRESS: _ClassVar[TaskStateRequest]
    TASK_STATE_REQUEST_COMPLETED: _ClassVar[TaskStateRequest]
    TASK_STATE_REQUEST_UNDO: _ClassVar[TaskStateRequest]
    TASK_STATE_REQUEST_ERROR: _ClassVar[TaskStateRequest]
TASK_STATE_REQUEST_UNSPECIFIED: TaskStateRequest
TASK_STATE_REQUEST_IN_PROGRESS: TaskStateRequest
TASK_STATE_REQUEST_COMPLETED: TaskStateRequest
TASK_STATE_REQUEST_UNDO: TaskStateRequest
TASK_STATE_REQUEST_ERROR: TaskStateRequest

class TaskStateChangeMessage(_message.Message):
    __slots__ = ("request_id", "instance_id", "task_id", "state")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    instance_id: str
    task_id: str
    state: TaskStateRequest
    def __init__(self, request_id: _Optional[str] = ..., instance_id: _Optional[str] = ..., task_id: _Optional[str] = ..., state: _Optional[_Union[TaskStateRequest, str]] = ...) -> None: ...

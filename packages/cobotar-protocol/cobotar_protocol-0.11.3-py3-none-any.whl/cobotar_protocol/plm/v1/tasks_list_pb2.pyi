from plm.v1 import task_pb2 as _task_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TasksForAgentRequest(_message.Message):
    __slots__ = ("request_id", "instance_id", "agent_id", "state")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    instance_id: str
    agent_id: str
    state: _task_pb2.TaskState
    def __init__(self, request_id: _Optional[str] = ..., instance_id: _Optional[str] = ..., agent_id: _Optional[str] = ..., state: _Optional[_Union[_task_pb2.TaskState, str]] = ...) -> None: ...

class TasksForAgentResponse(_message.Message):
    __slots__ = ("request_id", "instance_id", "agent_id", "task_ids")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_IDS_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    instance_id: str
    agent_id: str
    task_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, request_id: _Optional[str] = ..., instance_id: _Optional[str] = ..., agent_id: _Optional[str] = ..., task_ids: _Optional[_Iterable[str]] = ...) -> None: ...

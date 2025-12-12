from geometry.v1 import pose_pb2 as _pose_pb2
from plm.v1 import process_pb2 as _process_pb2
from plm.v1 import sequence_authoring_pb2 as _sequence_authoring_pb2
from plm.v1 import task_pb2 as _task_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StoredProcessMessage(_message.Message):
    __slots__ = ("id", "name", "description", "type", "frame", "root_sequence_id", "sequences", "tasks")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    FRAME_FIELD_NUMBER: _ClassVar[int]
    ROOT_SEQUENCE_ID_FIELD_NUMBER: _ClassVar[int]
    SEQUENCES_FIELD_NUMBER: _ClassVar[int]
    TASKS_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    type: _process_pb2.ProcessType
    frame: _pose_pb2.LocalizedPose
    root_sequence_id: str
    sequences: _containers.RepeatedCompositeFieldContainer[_sequence_authoring_pb2.StoredSequenceMessage]
    tasks: _containers.RepeatedCompositeFieldContainer[_task_pb2.TaskMessage]
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., type: _Optional[_Union[_process_pb2.ProcessType, str]] = ..., frame: _Optional[_Union[_pose_pb2.LocalizedPose, _Mapping]] = ..., root_sequence_id: _Optional[str] = ..., sequences: _Optional[_Iterable[_Union[_sequence_authoring_pb2.StoredSequenceMessage, _Mapping]]] = ..., tasks: _Optional[_Iterable[_Union[_task_pb2.TaskMessage, _Mapping]]] = ...) -> None: ...

class StoredProcessesMessage(_message.Message):
    __slots__ = ("processes",)
    PROCESSES_FIELD_NUMBER: _ClassVar[int]
    processes: _containers.RepeatedCompositeFieldContainer[StoredProcessMessage]
    def __init__(self, processes: _Optional[_Iterable[_Union[StoredProcessMessage, _Mapping]]] = ...) -> None: ...

class NewProcessMessage(_message.Message):
    __slots__ = ("name", "description", "type")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    type: _process_pb2.ProcessType
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., type: _Optional[_Union[_process_pb2.ProcessType, str]] = ...) -> None: ...

class UpdateProcessMessage(_message.Message):
    __slots__ = ("id", "name", "description", "type", "frame", "root_sequence_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    FRAME_FIELD_NUMBER: _ClassVar[int]
    ROOT_SEQUENCE_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    type: _process_pb2.ProcessType
    frame: _pose_pb2.LocalizedPose
    root_sequence_id: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., type: _Optional[_Union[_process_pb2.ProcessType, str]] = ..., frame: _Optional[_Union[_pose_pb2.LocalizedPose, _Mapping]] = ..., root_sequence_id: _Optional[str] = ...) -> None: ...

class DeleteProcessMessage(_message.Message):
    __slots__ = ("process_id",)
    PROCESS_ID_FIELD_NUMBER: _ClassVar[int]
    process_id: str
    def __init__(self, process_id: _Optional[str] = ...) -> None: ...

from geometry.v1 import pose_pb2 as _pose_pb2
from geometry.v1 import vector3_pb2 as _vector3_pb2
from plm.v1 import task_pb2 as _task_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StoredTaskMessage(_message.Message):
    __slots__ = ("id", "name", "description", "sequence_number", "part_id", "model_id", "task_type", "target", "approach", "assignment_preference")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    PART_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_TYPE_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    APPROACH_FIELD_NUMBER: _ClassVar[int]
    ASSIGNMENT_PREFERENCE_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    sequence_number: int
    part_id: str
    model_id: str
    task_type: _task_pb2.TaskType
    target: _pose_pb2.LocalizedPose
    approach: _vector3_pb2.Vector3
    assignment_preference: _task_pb2.TaskAssignmentPreference
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., sequence_number: _Optional[int] = ..., part_id: _Optional[str] = ..., model_id: _Optional[str] = ..., task_type: _Optional[_Union[_task_pb2.TaskType, str]] = ..., target: _Optional[_Union[_pose_pb2.LocalizedPose, _Mapping]] = ..., approach: _Optional[_Union[_vector3_pb2.Vector3, _Mapping]] = ..., assignment_preference: _Optional[_Union[_task_pb2.TaskAssignmentPreference, str]] = ...) -> None: ...

class NewTaskMessage(_message.Message):
    __slots__ = ("name", "description", "sequence_number", "parent_sequence_id")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    PARENT_SEQUENCE_ID_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    sequence_number: int
    parent_sequence_id: str
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., sequence_number: _Optional[int] = ..., parent_sequence_id: _Optional[str] = ...) -> None: ...

class UpdateTaskMessage(_message.Message):
    __slots__ = ("id", "name", "description", "sequence_number", "part_id", "model_id", "task_type", "target", "approach", "assignment_preference")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    PART_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_TYPE_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    APPROACH_FIELD_NUMBER: _ClassVar[int]
    ASSIGNMENT_PREFERENCE_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    sequence_number: int
    part_id: str
    model_id: str
    task_type: _task_pb2.TaskType
    target: _pose_pb2.LocalizedPose
    approach: _vector3_pb2.Vector3
    assignment_preference: _task_pb2.TaskAssignmentPreference
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., sequence_number: _Optional[int] = ..., part_id: _Optional[str] = ..., model_id: _Optional[str] = ..., task_type: _Optional[_Union[_task_pb2.TaskType, str]] = ..., target: _Optional[_Union[_pose_pb2.LocalizedPose, _Mapping]] = ..., approach: _Optional[_Union[_vector3_pb2.Vector3, _Mapping]] = ..., assignment_preference: _Optional[_Union[_task_pb2.TaskAssignmentPreference, str]] = ...) -> None: ...

class DeleteTaskMessage(_message.Message):
    __slots__ = ("task_id",)
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    def __init__(self, task_id: _Optional[str] = ...) -> None: ...

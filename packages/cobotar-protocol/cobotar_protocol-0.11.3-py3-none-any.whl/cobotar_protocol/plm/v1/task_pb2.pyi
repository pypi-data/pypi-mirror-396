from geometry.v1 import pose_pb2 as _pose_pb2
from geometry.v1 import vector3_pb2 as _vector3_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TaskState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TASK_STATE_UNSPECIFIED: _ClassVar[TaskState]
    TASK_STATE_MISSING_PRECONDITION: _ClassVar[TaskState]
    TASK_STATE_WAITING: _ClassVar[TaskState]
    TASK_STATE_IN_PROGRESS: _ClassVar[TaskState]
    TASK_STATE_COMPLETED: _ClassVar[TaskState]
    TASK_STATE_ERROR: _ClassVar[TaskState]

class TaskType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TASK_TYPE_UNSPECIFIED: _ClassVar[TaskType]
    TASK_TYPE_INSPECT: _ClassVar[TaskType]
    TASK_TYPE_FASTEN: _ClassVar[TaskType]
    TASK_TYPE_UNFASTEN: _ClassVar[TaskType]
    TASK_TYPE_MOUNT: _ClassVar[TaskType]
    TASK_TYPE_UNMOUNT: _ClassVar[TaskType]
    TASK_TYPE_MOVE: _ClassVar[TaskType]
    TASK_TYPE_REMOVE: _ClassVar[TaskType]
    TASK_TYPE_APPLY: _ClassVar[TaskType]
    TASK_TYPE_WIPE: _ClassVar[TaskType]

class TaskAssignmentPreference(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TASK_ASSIGNMENT_PREFERENCE_UNSPECIFIED: _ClassVar[TaskAssignmentPreference]
    TASK_ASSIGNMENT_PREFERENCE_PREFER_HUMAN: _ClassVar[TaskAssignmentPreference]
    TASK_ASSIGNMENT_PREFERENCE_ONLY_HUMAN: _ClassVar[TaskAssignmentPreference]
    TASK_ASSIGNMENT_PREFERENCE_PREFER_ROBOT: _ClassVar[TaskAssignmentPreference]
    TASK_ASSIGNMENT_PREFERENCE_ONLY_ROBOT: _ClassVar[TaskAssignmentPreference]
TASK_STATE_UNSPECIFIED: TaskState
TASK_STATE_MISSING_PRECONDITION: TaskState
TASK_STATE_WAITING: TaskState
TASK_STATE_IN_PROGRESS: TaskState
TASK_STATE_COMPLETED: TaskState
TASK_STATE_ERROR: TaskState
TASK_TYPE_UNSPECIFIED: TaskType
TASK_TYPE_INSPECT: TaskType
TASK_TYPE_FASTEN: TaskType
TASK_TYPE_UNFASTEN: TaskType
TASK_TYPE_MOUNT: TaskType
TASK_TYPE_UNMOUNT: TaskType
TASK_TYPE_MOVE: TaskType
TASK_TYPE_REMOVE: TaskType
TASK_TYPE_APPLY: TaskType
TASK_TYPE_WIPE: TaskType
TASK_ASSIGNMENT_PREFERENCE_UNSPECIFIED: TaskAssignmentPreference
TASK_ASSIGNMENT_PREFERENCE_PREFER_HUMAN: TaskAssignmentPreference
TASK_ASSIGNMENT_PREFERENCE_ONLY_HUMAN: TaskAssignmentPreference
TASK_ASSIGNMENT_PREFERENCE_PREFER_ROBOT: TaskAssignmentPreference
TASK_ASSIGNMENT_PREFERENCE_ONLY_ROBOT: TaskAssignmentPreference

class TaskMessage(_message.Message):
    __slots__ = ("id", "name", "description", "sequence_number", "part_id", "model_id", "task_type", "target", "approach", "parent_id", "agents_ids", "assigned_to", "state", "preconditions", "dependants", "assignment_preference", "can_reassign", "can_do", "can_undo")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    PART_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_TYPE_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    APPROACH_FIELD_NUMBER: _ClassVar[int]
    PARENT_ID_FIELD_NUMBER: _ClassVar[int]
    AGENTS_IDS_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    PRECONDITIONS_FIELD_NUMBER: _ClassVar[int]
    DEPENDANTS_FIELD_NUMBER: _ClassVar[int]
    ASSIGNMENT_PREFERENCE_FIELD_NUMBER: _ClassVar[int]
    CAN_REASSIGN_FIELD_NUMBER: _ClassVar[int]
    CAN_DO_FIELD_NUMBER: _ClassVar[int]
    CAN_UNDO_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    sequence_number: int
    part_id: str
    model_id: str
    task_type: TaskType
    target: _pose_pb2.LocalizedPose
    approach: _vector3_pb2.Vector3
    parent_id: str
    agents_ids: _containers.RepeatedScalarFieldContainer[str]
    assigned_to: str
    state: TaskState
    preconditions: _containers.RepeatedScalarFieldContainer[str]
    dependants: _containers.RepeatedScalarFieldContainer[str]
    assignment_preference: TaskAssignmentPreference
    can_reassign: bool
    can_do: bool
    can_undo: bool
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., sequence_number: _Optional[int] = ..., part_id: _Optional[str] = ..., model_id: _Optional[str] = ..., task_type: _Optional[_Union[TaskType, str]] = ..., target: _Optional[_Union[_pose_pb2.LocalizedPose, _Mapping]] = ..., approach: _Optional[_Union[_vector3_pb2.Vector3, _Mapping]] = ..., parent_id: _Optional[str] = ..., agents_ids: _Optional[_Iterable[str]] = ..., assigned_to: _Optional[str] = ..., state: _Optional[_Union[TaskState, str]] = ..., preconditions: _Optional[_Iterable[str]] = ..., dependants: _Optional[_Iterable[str]] = ..., assignment_preference: _Optional[_Union[TaskAssignmentPreference, str]] = ..., can_reassign: bool = ..., can_do: bool = ..., can_undo: bool = ...) -> None: ...

class TaskUpdatedMessage(_message.Message):
    __slots__ = ("id", "assigned_to", "state", "can_reassign", "can_do", "can_undo")
    ID_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    CAN_REASSIGN_FIELD_NUMBER: _ClassVar[int]
    CAN_DO_FIELD_NUMBER: _ClassVar[int]
    CAN_UNDO_FIELD_NUMBER: _ClassVar[int]
    id: str
    assigned_to: str
    state: TaskState
    can_reassign: bool
    can_do: bool
    can_undo: bool
    def __init__(self, id: _Optional[str] = ..., assigned_to: _Optional[str] = ..., state: _Optional[_Union[TaskState, str]] = ..., can_reassign: bool = ..., can_do: bool = ..., can_undo: bool = ...) -> None: ...

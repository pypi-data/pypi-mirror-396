from geometry.v1 import pose_pb2 as _pose_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SequenceState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SEQUENCE_STATE_UNSPECIFIED: _ClassVar[SequenceState]
    SEQUENCE_STATE_MISSING_PRECONDITION: _ClassVar[SequenceState]
    SEQUENCE_STATE_WAITING: _ClassVar[SequenceState]
    SEQUENCE_STATE_IN_PROGRESS: _ClassVar[SequenceState]
    SEQUENCE_STATE_COMPLETED: _ClassVar[SequenceState]
SEQUENCE_STATE_UNSPECIFIED: SequenceState
SEQUENCE_STATE_MISSING_PRECONDITION: SequenceState
SEQUENCE_STATE_WAITING: SequenceState
SEQUENCE_STATE_IN_PROGRESS: SequenceState
SEQUENCE_STATE_COMPLETED: SequenceState

class SequenceMessage(_message.Message):
    __slots__ = ("id", "name", "description", "sequence_number", "frame", "parent_id", "sequence_ids", "task_ids", "assigned_to", "state", "completed_tasks", "can_bulk_complete")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    FRAME_FIELD_NUMBER: _ClassVar[int]
    PARENT_ID_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_IDS_FIELD_NUMBER: _ClassVar[int]
    TASK_IDS_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_TASKS_FIELD_NUMBER: _ClassVar[int]
    CAN_BULK_COMPLETE_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    sequence_number: int
    frame: _pose_pb2.LocalizedPose
    parent_id: str
    sequence_ids: _containers.RepeatedScalarFieldContainer[str]
    task_ids: _containers.RepeatedScalarFieldContainer[str]
    assigned_to: _containers.RepeatedScalarFieldContainer[str]
    state: SequenceState
    completed_tasks: int
    can_bulk_complete: bool
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., sequence_number: _Optional[int] = ..., frame: _Optional[_Union[_pose_pb2.LocalizedPose, _Mapping]] = ..., parent_id: _Optional[str] = ..., sequence_ids: _Optional[_Iterable[str]] = ..., task_ids: _Optional[_Iterable[str]] = ..., assigned_to: _Optional[_Iterable[str]] = ..., state: _Optional[_Union[SequenceState, str]] = ..., completed_tasks: _Optional[int] = ..., can_bulk_complete: bool = ...) -> None: ...

class SequenceUpdatedMessage(_message.Message):
    __slots__ = ("sequence_id", "assigned_to", "state", "completed_tasks")
    SEQUENCE_ID_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_TASKS_FIELD_NUMBER: _ClassVar[int]
    sequence_id: str
    assigned_to: _containers.RepeatedScalarFieldContainer[str]
    state: SequenceState
    completed_tasks: int
    def __init__(self, sequence_id: _Optional[str] = ..., assigned_to: _Optional[_Iterable[str]] = ..., state: _Optional[_Union[SequenceState, str]] = ..., completed_tasks: _Optional[int] = ...) -> None: ...

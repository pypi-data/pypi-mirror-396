from geometry.v1 import pose_pb2 as _pose_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StoredSequenceMessage(_message.Message):
    __slots__ = ("id", "name", "description", "sequence_number", "frame", "parent_id", "sequence_ids", "task_ids", "can_bulk_complete")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    FRAME_FIELD_NUMBER: _ClassVar[int]
    PARENT_ID_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_IDS_FIELD_NUMBER: _ClassVar[int]
    TASK_IDS_FIELD_NUMBER: _ClassVar[int]
    CAN_BULK_COMPLETE_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    sequence_number: int
    frame: _pose_pb2.LocalizedPose
    parent_id: str
    sequence_ids: _containers.RepeatedScalarFieldContainer[str]
    task_ids: _containers.RepeatedScalarFieldContainer[str]
    can_bulk_complete: bool
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., sequence_number: _Optional[int] = ..., frame: _Optional[_Union[_pose_pb2.LocalizedPose, _Mapping]] = ..., parent_id: _Optional[str] = ..., sequence_ids: _Optional[_Iterable[str]] = ..., task_ids: _Optional[_Iterable[str]] = ..., can_bulk_complete: bool = ...) -> None: ...

class NewSequenceMessage(_message.Message):
    __slots__ = ("name", "description", "parent_id")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PARENT_ID_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    parent_id: str
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., parent_id: _Optional[str] = ...) -> None: ...

class UpdateSequenceMessage(_message.Message):
    __slots__ = ("id", "name", "description", "sequence_number", "frame", "parent_id", "sequence_ids", "task_ids", "can_bulk_complete")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    FRAME_FIELD_NUMBER: _ClassVar[int]
    PARENT_ID_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_IDS_FIELD_NUMBER: _ClassVar[int]
    TASK_IDS_FIELD_NUMBER: _ClassVar[int]
    CAN_BULK_COMPLETE_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    sequence_number: int
    frame: _pose_pb2.LocalizedPose
    parent_id: str
    sequence_ids: _containers.RepeatedScalarFieldContainer[str]
    task_ids: _containers.RepeatedScalarFieldContainer[str]
    can_bulk_complete: bool
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., sequence_number: _Optional[int] = ..., frame: _Optional[_Union[_pose_pb2.LocalizedPose, _Mapping]] = ..., parent_id: _Optional[str] = ..., sequence_ids: _Optional[_Iterable[str]] = ..., task_ids: _Optional[_Iterable[str]] = ..., can_bulk_complete: bool = ...) -> None: ...

class DeleteSequenceMessage(_message.Message):
    __slots__ = ("sequence_id",)
    SEQUENCE_ID_FIELD_NUMBER: _ClassVar[int]
    sequence_id: str
    def __init__(self, sequence_id: _Optional[str] = ...) -> None: ...

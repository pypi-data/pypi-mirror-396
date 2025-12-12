from ar.v1 import feedback_pb2 as _feedback_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FeedbackNewMessage(_message.Message):
    __slots__ = ("parent_config_id", "name", "icon", "description", "type", "frame_id", "agent_id")
    PARENT_CONFIG_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ICON_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    FRAME_ID_FIELD_NUMBER: _ClassVar[int]
    AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    parent_config_id: str
    name: str
    icon: str
    description: str
    type: _feedback_pb2.FeedbackType
    frame_id: str
    agent_id: str
    def __init__(self, parent_config_id: _Optional[str] = ..., name: _Optional[str] = ..., icon: _Optional[str] = ..., description: _Optional[str] = ..., type: _Optional[_Union[_feedback_pb2.FeedbackType, str]] = ..., frame_id: _Optional[str] = ..., agent_id: _Optional[str] = ...) -> None: ...

class FeedbackUpdateMessage(_message.Message):
    __slots__ = ("id", "name", "icon", "description")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ICON_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    icon: str
    description: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., icon: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class FeedbackCloneMessage(_message.Message):
    __slots__ = ("original_id", "name", "icon", "description")
    ORIGINAL_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ICON_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    original_id: str
    name: str
    icon: str
    description: str
    def __init__(self, original_id: _Optional[str] = ..., name: _Optional[str] = ..., icon: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class FeedbackDeleteMessage(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

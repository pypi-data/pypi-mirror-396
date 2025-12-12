from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ToolMessage(_message.Message):
    __slots__ = ("id", "name", "icon", "description", "model_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ICON_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    icon: str
    description: str
    model_id: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., icon: _Optional[str] = ..., description: _Optional[str] = ..., model_id: _Optional[str] = ...) -> None: ...

class ToolMessages(_message.Message):
    __slots__ = ("tools",)
    TOOLS_FIELD_NUMBER: _ClassVar[int]
    tools: _containers.RepeatedCompositeFieldContainer[ToolMessage]
    def __init__(self, tools: _Optional[_Iterable[_Union[ToolMessage, _Mapping]]] = ...) -> None: ...

class NewToolMessage(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class UpdateToolMessage(_message.Message):
    __slots__ = ("id", "name", "icon", "description", "model_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ICON_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    icon: str
    description: str
    model_id: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., icon: _Optional[str] = ..., description: _Optional[str] = ..., model_id: _Optional[str] = ...) -> None: ...

class DeleteToolMessage(_message.Message):
    __slots__ = ("tool_id",)
    TOOL_ID_FIELD_NUMBER: _ClassVar[int]
    tool_id: str
    def __init__(self, tool_id: _Optional[str] = ...) -> None: ...

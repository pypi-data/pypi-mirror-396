from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ModelMessage(_message.Message):
    __slots__ = ("id", "url")
    ID_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    id: str
    url: str
    def __init__(self, id: _Optional[str] = ..., url: _Optional[str] = ...) -> None: ...

class ModelMessages(_message.Message):
    __slots__ = ("models",)
    MODELS_FIELD_NUMBER: _ClassVar[int]
    models: _containers.RepeatedCompositeFieldContainer[ModelMessage]
    def __init__(self, models: _Optional[_Iterable[_Union[ModelMessage, _Mapping]]] = ...) -> None: ...

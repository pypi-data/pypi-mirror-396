from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Capability(_message.Message):
    __slots__ = ("agent_id", "part_id", "estimated_time")
    AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    PART_ID_FIELD_NUMBER: _ClassVar[int]
    ESTIMATED_TIME_FIELD_NUMBER: _ClassVar[int]
    agent_id: str
    part_id: str
    estimated_time: int
    def __init__(self, agent_id: _Optional[str] = ..., part_id: _Optional[str] = ..., estimated_time: _Optional[int] = ...) -> None: ...

class Capabilities(_message.Message):
    __slots__ = ("capabilities",)
    CAPABILITIES_FIELD_NUMBER: _ClassVar[int]
    capabilities: _containers.RepeatedCompositeFieldContainer[Capability]
    def __init__(self, capabilities: _Optional[_Iterable[_Union[Capability, _Mapping]]] = ...) -> None: ...

from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ChatRequest(_message.Message):
    __slots__ = ("input", "user", "session_id", "metadata")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    INPUT_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    input: str
    user: str
    session_id: str
    metadata: _containers.ScalarMap[str, str]
    def __init__(self, input: _Optional[str] = ..., user: _Optional[str] = ..., session_id: _Optional[str] = ..., metadata: _Optional[_Mapping[str, str]] = ...) -> None: ...

class ChatResponse(_message.Message):
    __slots__ = ("chunk", "is_last")
    CHUNK_FIELD_NUMBER: _ClassVar[int]
    IS_LAST_FIELD_NUMBER: _ClassVar[int]
    chunk: str
    is_last: bool
    def __init__(self, chunk: _Optional[str] = ..., is_last: bool = ...) -> None: ...

class CreateSessionRequest(_message.Message):
    __slots__ = ("user", "metadata")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    USER_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    user: str
    metadata: _containers.ScalarMap[str, str]
    def __init__(self, user: _Optional[str] = ..., metadata: _Optional[_Mapping[str, str]] = ...) -> None: ...

class CreateSessionResponse(_message.Message):
    __slots__ = ("_id", "user", "summary", "scoreLevel", "createdAt", "updatedAt")
    _ID_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    SCORELEVEL_FIELD_NUMBER: _ClassVar[int]
    CREATEDAT_FIELD_NUMBER: _ClassVar[int]
    UPDATEDAT_FIELD_NUMBER: _ClassVar[int]
    _id: str
    user: str
    summary: str
    scoreLevel: int
    createdAt: str
    updatedAt: str
    def __init__(self, _id: _Optional[str] = ..., user: _Optional[str] = ..., summary: _Optional[str] = ..., scoreLevel: _Optional[int] = ..., createdAt: _Optional[str] = ..., updatedAt: _Optional[str] = ...) -> None: ...

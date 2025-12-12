from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class TextErrorCorrectionRequest(_message.Message):
    __slots__ = ("texts",)
    TEXTS_FIELD_NUMBER: _ClassVar[int]
    texts: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, texts: _Optional[_Iterable[str]] = ...) -> None: ...

class TextErrorCorrectionResponse(_message.Message):
    __slots__ = ("code", "message", "detail", "data")
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    DETAIL_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    code: int
    message: str
    detail: str
    data: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, code: _Optional[int] = ..., message: _Optional[str] = ..., detail: _Optional[str] = ..., data: _Optional[_Iterable[str]] = ...) -> None: ...

class SegRequest(_message.Message):
    __slots__ = ("text",)
    TEXT_FIELD_NUMBER: _ClassVar[int]
    text: str
    def __init__(self, text: _Optional[str] = ...) -> None: ...

class SegResponse(_message.Message):
    __slots__ = ("code", "message", "detail", "data")
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    DETAIL_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    code: int
    message: str
    detail: str
    data: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, code: _Optional[int] = ..., message: _Optional[str] = ..., detail: _Optional[str] = ..., data: _Optional[_Iterable[str]] = ...) -> None: ...

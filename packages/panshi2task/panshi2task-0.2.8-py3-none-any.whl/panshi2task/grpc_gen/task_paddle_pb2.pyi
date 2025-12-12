from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BytesOCRRequest(_message.Message):
    __slots__ = ("file_name", "chunk_data")
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    CHUNK_DATA_FIELD_NUMBER: _ClassVar[int]
    file_name: str
    chunk_data: bytes
    def __init__(self, file_name: _Optional[str] = ..., chunk_data: _Optional[bytes] = ...) -> None: ...

class OCRRequest(_message.Message):
    __slots__ = ("file_path", "file_name")
    FILE_PATH_FIELD_NUMBER: _ClassVar[int]
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    file_path: str
    file_name: str
    def __init__(self, file_path: _Optional[str] = ..., file_name: _Optional[str] = ...) -> None: ...

class OCRResponse(_message.Message):
    __slots__ = ("page_num", "contents")
    PAGE_NUM_FIELD_NUMBER: _ClassVar[int]
    CONTENTS_FIELD_NUMBER: _ClassVar[int]
    page_num: int
    contents: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, page_num: _Optional[int] = ..., contents: _Optional[_Iterable[str]] = ...) -> None: ...

class BytesStructureRequest(_message.Message):
    __slots__ = ("file_name", "chunk_data")
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    CHUNK_DATA_FIELD_NUMBER: _ClassVar[int]
    file_name: str
    chunk_data: bytes
    def __init__(self, file_name: _Optional[str] = ..., chunk_data: _Optional[bytes] = ...) -> None: ...

class StructureRequest(_message.Message):
    __slots__ = ("file_path", "file_name")
    FILE_PATH_FIELD_NUMBER: _ClassVar[int]
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    file_path: str
    file_name: str
    def __init__(self, file_path: _Optional[str] = ..., file_name: _Optional[str] = ...) -> None: ...

class StructureResponse(_message.Message):
    __slots__ = ("type", "res", "img_url", "page_num")
    class Item(_message.Message):
        __slots__ = ("confidence", "text", "table_html")
        CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
        TEXT_FIELD_NUMBER: _ClassVar[int]
        TABLE_HTML_FIELD_NUMBER: _ClassVar[int]
        confidence: float
        text: str
        table_html: str
        def __init__(self, confidence: _Optional[float] = ..., text: _Optional[str] = ..., table_html: _Optional[str] = ...) -> None: ...
    TYPE_FIELD_NUMBER: _ClassVar[int]
    RES_FIELD_NUMBER: _ClassVar[int]
    IMG_URL_FIELD_NUMBER: _ClassVar[int]
    PAGE_NUM_FIELD_NUMBER: _ClassVar[int]
    type: str
    res: _containers.RepeatedCompositeFieldContainer[StructureResponse.Item]
    img_url: str
    page_num: int
    def __init__(self, type: _Optional[str] = ..., res: _Optional[_Iterable[_Union[StructureResponse.Item, _Mapping]]] = ..., img_url: _Optional[str] = ..., page_num: _Optional[int] = ...) -> None: ...

class EntityExtractRequest(_message.Message):
    __slots__ = ("schema", "inputs")
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    schema: _containers.RepeatedScalarFieldContainer[str]
    inputs: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, schema: _Optional[_Iterable[str]] = ..., inputs: _Optional[_Iterable[str]] = ...) -> None: ...

class EntityExtractResponse(_message.Message):
    __slots__ = ("code", "message", "detail", "data")
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    DETAIL_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    code: int
    message: str
    detail: str
    data: str
    def __init__(self, code: _Optional[int] = ..., message: _Optional[str] = ..., detail: _Optional[str] = ..., data: _Optional[str] = ...) -> None: ...

class RelationExtractRequest(_message.Message):
    __slots__ = ("schema", "inputs")
    class SchemaEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _struct_pb2.ListValue
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_struct_pb2.ListValue, _Mapping]] = ...) -> None: ...
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    schema: _containers.MessageMap[str, _struct_pb2.ListValue]
    inputs: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, schema: _Optional[_Mapping[str, _struct_pb2.ListValue]] = ..., inputs: _Optional[_Iterable[str]] = ...) -> None: ...

class RelationExtractResponse(_message.Message):
    __slots__ = ("code", "message", "detail", "data")
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    DETAIL_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    code: int
    message: str
    detail: str
    data: str
    def __init__(self, code: _Optional[int] = ..., message: _Optional[str] = ..., detail: _Optional[str] = ..., data: _Optional[str] = ...) -> None: ...

from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RerankRequest(_message.Message):
    __slots__ = ("query", "texts", "truncate", "raw_scores", "return_text")
    QUERY_FIELD_NUMBER: _ClassVar[int]
    TEXTS_FIELD_NUMBER: _ClassVar[int]
    TRUNCATE_FIELD_NUMBER: _ClassVar[int]
    RAW_SCORES_FIELD_NUMBER: _ClassVar[int]
    RETURN_TEXT_FIELD_NUMBER: _ClassVar[int]
    query: str
    texts: _containers.RepeatedScalarFieldContainer[str]
    truncate: bool
    raw_scores: bool
    return_text: bool
    def __init__(self, query: _Optional[str] = ..., texts: _Optional[_Iterable[str]] = ..., truncate: bool = ..., raw_scores: bool = ..., return_text: bool = ...) -> None: ...

class Rank(_message.Message):
    __slots__ = ("text", "score")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    text: str
    score: float
    def __init__(self, text: _Optional[str] = ..., score: _Optional[float] = ...) -> None: ...

class RerankResponse(_message.Message):
    __slots__ = ("ranks",)
    RANKS_FIELD_NUMBER: _ClassVar[int]
    ranks: _containers.RepeatedCompositeFieldContainer[Rank]
    def __init__(self, ranks: _Optional[_Iterable[_Union[Rank, _Mapping]]] = ...) -> None: ...

class EmbedRequest(_message.Message):
    __slots__ = ("input", "max_length")
    INPUT_FIELD_NUMBER: _ClassVar[int]
    MAX_LENGTH_FIELD_NUMBER: _ClassVar[int]
    input: str
    max_length: int
    def __init__(self, input: _Optional[str] = ..., max_length: _Optional[int] = ...) -> None: ...

class EmbedResponse(_message.Message):
    __slots__ = ("embeddings",)
    EMBEDDINGS_FIELD_NUMBER: _ClassVar[int]
    embeddings: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, embeddings: _Optional[_Iterable[float]] = ...) -> None: ...

class BatchEmbedRequest(_message.Message):
    __slots__ = ("inputs", "batch_size", "max_length")
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    BATCH_SIZE_FIELD_NUMBER: _ClassVar[int]
    MAX_LENGTH_FIELD_NUMBER: _ClassVar[int]
    inputs: _containers.RepeatedScalarFieldContainer[str]
    batch_size: int
    max_length: int
    def __init__(self, inputs: _Optional[_Iterable[str]] = ..., batch_size: _Optional[int] = ..., max_length: _Optional[int] = ...) -> None: ...

class Embedding(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, values: _Optional[_Iterable[float]] = ...) -> None: ...

class BatchEmbedResponse(_message.Message):
    __slots__ = ("embeddings",)
    EMBEDDINGS_FIELD_NUMBER: _ClassVar[int]
    embeddings: _containers.RepeatedCompositeFieldContainer[Embedding]
    def __init__(self, embeddings: _Optional[_Iterable[_Union[Embedding, _Mapping]]] = ...) -> None: ...

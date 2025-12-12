from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EntityMiniingRequest(_message.Message):
    __slots__ = ("schema", "text", "except_num")
    class SchemaItem(_message.Message):
        __slots__ = ("name", "desc")
        NAME_FIELD_NUMBER: _ClassVar[int]
        DESC_FIELD_NUMBER: _ClassVar[int]
        name: str
        desc: str
        def __init__(self, name: _Optional[str] = ..., desc: _Optional[str] = ...) -> None: ...
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    EXCEPT_NUM_FIELD_NUMBER: _ClassVar[int]
    schema: _containers.RepeatedCompositeFieldContainer[EntityMiniingRequest.SchemaItem]
    text: str
    except_num: int
    def __init__(self, schema: _Optional[_Iterable[_Union[EntityMiniingRequest.SchemaItem, _Mapping]]] = ..., text: _Optional[str] = ..., except_num: _Optional[int] = ...) -> None: ...

class EntityMiniingResponse(_message.Message):
    __slots__ = ("code", "message", "detail", "data")
    class DataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _struct_pb2.ListValue
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_struct_pb2.ListValue, _Mapping]] = ...) -> None: ...
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    DETAIL_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    code: int
    message: str
    detail: str
    data: _containers.MessageMap[str, _struct_pb2.ListValue]
    def __init__(self, code: _Optional[int] = ..., message: _Optional[str] = ..., detail: _Optional[str] = ..., data: _Optional[_Mapping[str, _struct_pb2.ListValue]] = ...) -> None: ...

class EntityMiniingBatchRequest(_message.Message):
    __slots__ = ("entities",)
    ENTITIES_FIELD_NUMBER: _ClassVar[int]
    entities: _containers.RepeatedCompositeFieldContainer[EntityMiniingRequest]
    def __init__(self, entities: _Optional[_Iterable[_Union[EntityMiniingRequest, _Mapping]]] = ...) -> None: ...

class EntityMiniingBatchResponse(_message.Message):
    __slots__ = ("code", "message", "detail", "data")
    class EntityResult(_message.Message):
        __slots__ = ("data",)
        class DataEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: str
            value: _struct_pb2.ListValue
            def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_struct_pb2.ListValue, _Mapping]] = ...) -> None: ...
        DATA_FIELD_NUMBER: _ClassVar[int]
        data: _containers.MessageMap[str, _struct_pb2.ListValue]
        def __init__(self, data: _Optional[_Mapping[str, _struct_pb2.ListValue]] = ...) -> None: ...
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    DETAIL_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    code: int
    message: str
    detail: str
    data: _containers.RepeatedCompositeFieldContainer[EntityMiniingBatchResponse.EntityResult]
    def __init__(self, code: _Optional[int] = ..., message: _Optional[str] = ..., detail: _Optional[str] = ..., data: _Optional[_Iterable[_Union[EntityMiniingBatchResponse.EntityResult, _Mapping]]] = ...) -> None: ...

class FAQMiniingRequest(_message.Message):
    __slots__ = ("text", "except_num")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    EXCEPT_NUM_FIELD_NUMBER: _ClassVar[int]
    text: str
    except_num: int
    def __init__(self, text: _Optional[str] = ..., except_num: _Optional[int] = ...) -> None: ...

class FAQMiniingResponse(_message.Message):
    __slots__ = ("code", "message", "detail", "data")
    class QAItem(_message.Message):
        __slots__ = ("query", "answer")
        QUERY_FIELD_NUMBER: _ClassVar[int]
        ANSWER_FIELD_NUMBER: _ClassVar[int]
        query: str
        answer: str
        def __init__(self, query: _Optional[str] = ..., answer: _Optional[str] = ...) -> None: ...
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    DETAIL_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    code: int
    message: str
    detail: str
    data: _containers.RepeatedCompositeFieldContainer[FAQMiniingResponse.QAItem]
    def __init__(self, code: _Optional[int] = ..., message: _Optional[str] = ..., detail: _Optional[str] = ..., data: _Optional[_Iterable[_Union[FAQMiniingResponse.QAItem, _Mapping]]] = ...) -> None: ...

class FAQMiniingBatchRequest(_message.Message):
    __slots__ = ("faqs",)
    FAQS_FIELD_NUMBER: _ClassVar[int]
    faqs: _containers.RepeatedCompositeFieldContainer[FAQMiniingRequest]
    def __init__(self, faqs: _Optional[_Iterable[_Union[FAQMiniingRequest, _Mapping]]] = ...) -> None: ...

class FAQResult(_message.Message):
    __slots__ = ("data",)
    class QAItem(_message.Message):
        __slots__ = ("query", "answer")
        QUERY_FIELD_NUMBER: _ClassVar[int]
        ANSWER_FIELD_NUMBER: _ClassVar[int]
        query: str
        answer: str
        def __init__(self, query: _Optional[str] = ..., answer: _Optional[str] = ...) -> None: ...
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: _containers.RepeatedCompositeFieldContainer[FAQResult.QAItem]
    def __init__(self, data: _Optional[_Iterable[_Union[FAQResult.QAItem, _Mapping]]] = ...) -> None: ...

class FAQMiniingBatchResponse(_message.Message):
    __slots__ = ("code", "message", "detail", "data")
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    DETAIL_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    code: int
    message: str
    detail: str
    data: _containers.RepeatedCompositeFieldContainer[FAQResult]
    def __init__(self, code: _Optional[int] = ..., message: _Optional[str] = ..., detail: _Optional[str] = ..., data: _Optional[_Iterable[_Union[FAQResult, _Mapping]]] = ...) -> None: ...

class QuestionGenRequest(_message.Message):
    __slots__ = ("text", "except_num")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    EXCEPT_NUM_FIELD_NUMBER: _ClassVar[int]
    text: str
    except_num: int
    def __init__(self, text: _Optional[str] = ..., except_num: _Optional[int] = ...) -> None: ...

class QuestionGenResponse(_message.Message):
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

class QuestionGenBatchRequest(_message.Message):
    __slots__ = ("question_gens",)
    QUESTION_GENS_FIELD_NUMBER: _ClassVar[int]
    question_gens: _containers.RepeatedCompositeFieldContainer[QuestionGenRequest]
    def __init__(self, question_gens: _Optional[_Iterable[_Union[QuestionGenRequest, _Mapping]]] = ...) -> None: ...

class QuestionGenBatchResponse(_message.Message):
    __slots__ = ("code", "message", "detail", "data")
    class QuestionResult(_message.Message):
        __slots__ = ("data",)
        DATA_FIELD_NUMBER: _ClassVar[int]
        data: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, data: _Optional[_Iterable[str]] = ...) -> None: ...
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    DETAIL_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    code: int
    message: str
    detail: str
    data: _containers.RepeatedCompositeFieldContainer[QuestionGenBatchResponse.QuestionResult]
    def __init__(self, code: _Optional[int] = ..., message: _Optional[str] = ..., detail: _Optional[str] = ..., data: _Optional[_Iterable[_Union[QuestionGenBatchResponse.QuestionResult, _Mapping]]] = ...) -> None: ...

class SummaryRequest(_message.Message):
    __slots__ = ("text",)
    TEXT_FIELD_NUMBER: _ClassVar[int]
    text: str
    def __init__(self, text: _Optional[str] = ...) -> None: ...

class SummaryResponse(_message.Message):
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

class SummaryBatchRequest(_message.Message):
    __slots__ = ("texts",)
    TEXTS_FIELD_NUMBER: _ClassVar[int]
    texts: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, texts: _Optional[_Iterable[str]] = ...) -> None: ...

class SummaryBatchResponse(_message.Message):
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

class TableSummaryRequest(_message.Message):
    __slots__ = ("text",)
    TEXT_FIELD_NUMBER: _ClassVar[int]
    text: str
    def __init__(self, text: _Optional[str] = ...) -> None: ...

class TableSummaryResponse(_message.Message):
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

class TableSummaryBatchRequest(_message.Message):
    __slots__ = ("texts",)
    TEXTS_FIELD_NUMBER: _ClassVar[int]
    texts: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, texts: _Optional[_Iterable[str]] = ...) -> None: ...

class TableSummaryBatchResponse(_message.Message):
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

class TopicMiningRequest(_message.Message):
    __slots__ = ("titles", "summary", "except_num")
    TITLES_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    EXCEPT_NUM_FIELD_NUMBER: _ClassVar[int]
    titles: _containers.RepeatedScalarFieldContainer[str]
    summary: str
    except_num: int
    def __init__(self, titles: _Optional[_Iterable[str]] = ..., summary: _Optional[str] = ..., except_num: _Optional[int] = ...) -> None: ...

class TopicMiningResponse(_message.Message):
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

class TopicMiningBatchRequest(_message.Message):
    __slots__ = ("topics",)
    TOPICS_FIELD_NUMBER: _ClassVar[int]
    topics: _containers.RepeatedCompositeFieldContainer[TopicMiningRequest]
    def __init__(self, topics: _Optional[_Iterable[_Union[TopicMiningRequest, _Mapping]]] = ...) -> None: ...

class TopicMiningBatchResponse(_message.Message):
    __slots__ = ("code", "message", "detail", "data")
    class TopicResult(_message.Message):
        __slots__ = ("data",)
        DATA_FIELD_NUMBER: _ClassVar[int]
        data: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, data: _Optional[_Iterable[str]] = ...) -> None: ...
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    DETAIL_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    code: int
    message: str
    detail: str
    data: _containers.RepeatedCompositeFieldContainer[TopicMiningBatchResponse.TopicResult]
    def __init__(self, code: _Optional[int] = ..., message: _Optional[str] = ..., detail: _Optional[str] = ..., data: _Optional[_Iterable[_Union[TopicMiningBatchResponse.TopicResult, _Mapping]]] = ...) -> None: ...

class TranslateRequest(_message.Message):
    __slots__ = ("to_language", "text")
    TO_LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    to_language: str
    text: str
    def __init__(self, to_language: _Optional[str] = ..., text: _Optional[str] = ...) -> None: ...

class TranslateBatchRequest(_message.Message):
    __slots__ = ("to_language", "text")
    TO_LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    to_language: str
    text: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, to_language: _Optional[str] = ..., text: _Optional[_Iterable[str]] = ...) -> None: ...

class TranslateResponse(_message.Message):
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

class TranslateBatchResponse(_message.Message):
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

class GenerateCateRequest(_message.Message):
    __slots__ = ("fileid", "filename", "keyword", "summary", "cates")
    FILEID_FIELD_NUMBER: _ClassVar[int]
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    KEYWORD_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    CATES_FIELD_NUMBER: _ClassVar[int]
    fileid: str
    filename: str
    keyword: str
    summary: str
    cates: str
    def __init__(self, fileid: _Optional[str] = ..., filename: _Optional[str] = ..., keyword: _Optional[str] = ..., summary: _Optional[str] = ..., cates: _Optional[str] = ...) -> None: ...

class GenerateCateResponse(_message.Message):
    __slots__ = ("cates", "source", "fileid")
    CATES_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    FILEID_FIELD_NUMBER: _ClassVar[int]
    cates: _containers.RepeatedScalarFieldContainer[str]
    source: str
    fileid: str
    def __init__(self, cates: _Optional[_Iterable[str]] = ..., source: _Optional[str] = ..., fileid: _Optional[str] = ...) -> None: ...

class GenerateCateBatchRequest(_message.Message):
    __slots__ = ("generate_cate_requests",)
    GENERATE_CATE_REQUESTS_FIELD_NUMBER: _ClassVar[int]
    generate_cate_requests: _containers.RepeatedCompositeFieldContainer[GenerateCateRequest]
    def __init__(self, generate_cate_requests: _Optional[_Iterable[_Union[GenerateCateRequest, _Mapping]]] = ...) -> None: ...

class GenerateCateBatchResponse(_message.Message):
    __slots__ = ("generate_cate_responses",)
    GENERATE_CATE_RESPONSES_FIELD_NUMBER: _ClassVar[int]
    generate_cate_responses: _containers.RepeatedCompositeFieldContainer[GenerateCateResponse]
    def __init__(self, generate_cate_responses: _Optional[_Iterable[_Union[GenerateCateResponse, _Mapping]]] = ...) -> None: ...

class DeriveSubCategoryRequest(_message.Message):
    __slots__ = ("fileNames", "primaryCategory")
    FILENAMES_FIELD_NUMBER: _ClassVar[int]
    PRIMARYCATEGORY_FIELD_NUMBER: _ClassVar[int]
    fileNames: str
    primaryCategory: str
    def __init__(self, fileNames: _Optional[str] = ..., primaryCategory: _Optional[str] = ...) -> None: ...

class DeriveSubCategoryResponse(_message.Message):
    __slots__ = ("code", "message", "detail", "data")
    class DataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _struct_pb2.ListValue
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_struct_pb2.ListValue, _Mapping]] = ...) -> None: ...
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    DETAIL_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    code: int
    message: str
    detail: str
    data: _containers.MessageMap[str, _struct_pb2.ListValue]
    def __init__(self, code: _Optional[int] = ..., message: _Optional[str] = ..., detail: _Optional[str] = ..., data: _Optional[_Mapping[str, _struct_pb2.ListValue]] = ...) -> None: ...

class AggregateSubCategoryRequest(_message.Message):
    __slots__ = ("subcategory",)
    SUBCATEGORY_FIELD_NUMBER: _ClassVar[int]
    subcategory: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, subcategory: _Optional[_Iterable[str]] = ...) -> None: ...

class AggregateSubCategoryResponse(_message.Message):
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

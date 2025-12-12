import json
import os
from typing import Iterable, List, Optional, Dict

import grpc
from google.protobuf.json_format import MessageToDict, ParseDict
from loguru import logger
from pydantic import BaseModel, Field

from panshi2task.base import common_grpc_opts
from panshi2task.grpc_gen.task_paddle_pb2 import OCRRequest, StructureRequest, EntityExtractRequest, \
    EntityExtractResponse, RelationExtractResponse, RelationExtractRequest, BytesOCRRequest, BytesStructureRequest
from panshi2task.grpc_gen.task_paddle_pb2_grpc import OCRStub, StructureStub, InformationExtractStub


class OcrPageResult(BaseModel):
    page_num: int
    contents: List[str]


class Item(BaseModel):
    confidence: Optional[float] = None
    text: Optional[str] = Field(default=None)
    table_html: Optional[str] = Field(default=None)


class BoxRecItem(BaseModel):
    type: str
    res: List[Item] | None = None
    img_url: Optional[str] = Field(default=None, description="通过bbox切分原图获取的图片,并上传值minio后的url地址")
    page_num: int


class PaddleTaskClient:
    def __init__(self, url: str):
        self.url = url
        opts = common_grpc_opts
        self.channel = grpc.insecure_channel(url, options=opts)
        self._ocr_stub = OCRStub(self.channel)
        self._structure_stub = StructureStub(self.channel)
        self._ie_stub = InformationExtractStub(self.channel)
        logger.info("paddle client 初始化完成...")

    @staticmethod
    def get_ocr_request_itr(local_file_path: str):
        chunk_size = 1024
        file_name_with_ext = os.path.basename(local_file_path)
        with open(local_file_path, mode="rb") as f:
            yield BytesOCRRequest(file_name=file_name_with_ext)
            while True:
                chunk = f.read(chunk_size)
                if chunk:
                    yield BytesOCRRequest(chunk_data=chunk)
                else:
                    return

    @staticmethod
    def get_structure_request_itr(local_file_path: str):
        chunk_size = 1024
        file_name_with_ext = os.path.basename(local_file_path)
        with open(local_file_path, mode="rb") as f:
            yield BytesStructureRequest(file_name=file_name_with_ext)
            while True:
                chunk = f.read(chunk_size)
                if chunk:
                    yield BytesStructureRequest(chunk_data=chunk)
                else:
                    return

    def image_ocr(self, file_path: str, file_name: str | None = None) -> OcrPageResult:
        req = OCRRequest(file_path=file_path, file_name=file_name)
        _itr = self._ocr_stub.RecStream(req)
        result = None
        for item in _itr:
            result = OcrPageResult.model_validate(MessageToDict(item, preserving_proto_field_name=True))
            continue
        return result

    def image_ocr_bytes(self, local_file_path: str) -> OcrPageResult:
        request_iterator = self.get_ocr_request_itr(local_file_path)
        _itr = self._ocr_stub.BytesRecStream(request_iterator)
        result = None
        for item in _itr:
            result = OcrPageResult.model_validate(MessageToDict(item, preserving_proto_field_name=True))
            continue
        return result

    def pdf_ocr(self, file_path: str, file_name: str | None = None) -> Iterable[OcrPageResult]:
        req = OCRRequest(file_path=file_path, file_name=file_name)
        _itr = self._ocr_stub.RecStream(req)
        for item in _itr:
            yield OcrPageResult.model_validate(MessageToDict(item, preserving_proto_field_name=True))

    def pdf_ocr_bytes(self, local_file_path: str) -> Iterable[OcrPageResult]:
        request_iterator = self.get_ocr_request_itr(local_file_path)
        _itr = self._ocr_stub.BytesRecStream(request_iterator)
        for item in _itr:
            yield OcrPageResult.model_validate(MessageToDict(item, preserving_proto_field_name=True))

    def pdf_structure(self, file_path: str, file_name: str | None = None) -> Iterable[BoxRecItem]:
        req = StructureRequest(file_path=file_path, file_name=file_name)
        _itr = self._structure_stub.AnalyseStream(req)
        for item in _itr:
            yield BoxRecItem.model_validate(MessageToDict(item, preserving_proto_field_name=True))

    def pdf_structure_bytes(self, local_file_path: str) -> Iterable[BoxRecItem]:
        request_iterator = self.get_structure_request_itr(local_file_path)
        _itr = self._structure_stub.BytesAnalyseStream(request_iterator)
        for item in _itr:
            yield BoxRecItem.model_validate(MessageToDict(item, preserving_proto_field_name=True))

    def entity_extract(self, schema: List[str], inputs: List[str]) -> List[Dict]:
        req = ParseDict({"schema": schema, "inputs": inputs}, EntityExtractRequest())
        resp: EntityExtractResponse = self._ie_stub.EntityExtract(req)
        if resp.code == 200:
            data_str = MessageToDict(resp)["data"]
            return json.loads(data_str)
        else:
            return []

    def relation_extract(self, schema: Dict, inputs: List[str]) -> List[Dict]:
        req = ParseDict({"schema": schema, "inputs": inputs}, RelationExtractRequest())
        resp: RelationExtractResponse = self._ie_stub.RelationExtract(req)
        if resp.code == 200:
            data_str = MessageToDict(resp)["data"]
            return json.loads(data_str)
        else:
            return []

    def close(self):
        if self.channel:
            self.channel.close()

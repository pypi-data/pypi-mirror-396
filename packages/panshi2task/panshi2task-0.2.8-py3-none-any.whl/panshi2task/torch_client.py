from typing import List

import grpc
from google.protobuf.json_format import ParseDict, MessageToDict
from loguru import logger

from panshi2task.base import common_grpc_opts, DPLUS_3_4_GRPC_SERVER
from panshi2task.grpc_gen.task_torch_pb2 import TextErrorCorrectionRequest, TextErrorCorrectionResponse, SegRequest
from panshi2task.grpc_gen.task_torch_pb2_grpc import SegStub, TextErrorCorrectionStub


class TorchTaskClient:
    def __init__(self, url: str):
        self.url = url
        opts = common_grpc_opts
        self.channel = grpc.insecure_channel(url, options=opts)
        self._seg_stub = SegStub(self.channel)
        self._error_stub = TextErrorCorrectionStub(self.channel)
        logger.info("torch client 初始化完成...")

    def text_error_correction(self, texts: List[str]) -> List[str]:
        req = ParseDict({"texts": texts}, TextErrorCorrectionRequest())
        resp: TextErrorCorrectionResponse = self._error_stub.excute(req)
        if resp.code == 200:
            return MessageToDict(resp)["data"]
        else:
            logger.error("message:{},detail:{}", resp.message, resp.detail)
            return texts

    def doc_seg(self, text: str) -> List[str]:
        req = SegRequest(text=text)
        resp = self._seg_stub.excute(req)
        if resp.code == 200:
            return MessageToDict(resp)["data"]
        else:
            logger.error("message:{},detail:{}", resp.message, resp.detail)
            return text

    def close(self):
        if self.channel:
            self.channel.close()
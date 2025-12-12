from typing import List

import grpc
from google.protobuf.json_format import MessageToDict, ParseDict
from loguru import logger
from pydantic import BaseModel

from panshi2task.base import common_grpc_opts
from panshi2task.grpc_gen.task_embedding_pb2 import RerankRequest, RerankResponse
from panshi2task.grpc_gen.task_embedding_pb2_grpc import RerankStub


class RankItem(BaseModel):
    text: str | None
    score: float


class RerankTaskClient:
    def __init__(self, url: str):
        self.url = url
        opts = common_grpc_opts
        self.channel = grpc.insecure_channel(url, options=opts)
        self.stub = RerankStub(self.channel)
        logger.info("rerank client 初始化完成...")

    def _rerank(self, req: RerankRequest) -> RerankResponse:
        return self.stub.Rerank(req)

    def rerank(self, query: str, texts: List[str], truncate: bool = True, raw_scores: bool = False,
               return_text: bool = True) -> List[RankItem]:
        _dict_in = {
            "query": query,
            "texts": texts,
            "truncate": truncate,
            "raw_scores": raw_scores,
            "return_text": return_text,
        }
        req: RerankRequest = ParseDict(_dict_in, RerankRequest())
        resp = self._rerank(req)
        _dict_out = MessageToDict(resp)
        return [RankItem.model_validate(item) for item in _dict_out["ranks"]]

    def close(self):
        if self.channel:
            self.channel.close()

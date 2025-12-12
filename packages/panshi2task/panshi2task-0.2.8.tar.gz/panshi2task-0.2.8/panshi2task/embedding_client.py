from typing import List

import grpc
import numpy as np
from google.protobuf.json_format import MessageToDict
from loguru import logger
from sklearn.metrics.pairwise import cosine_similarity

from panshi2task.base import common_grpc_opts
from panshi2task.grpc_gen.task_embedding_pb2 import EmbedRequest, EmbedResponse, BatchEmbedRequest, BatchEmbedResponse
from panshi2task.grpc_gen.task_embedding_pb2_grpc import EmbedStub


def find_most_similar_vector(query_vector, vector_list):
    max_similarity = -1
    most_similar_index = None
    query_vector = np.array(query_vector).reshape(1, -1)
    for idx, vector in enumerate(vector_list):
        vector = np.array(vector).reshape(1, -1)
        similarity = cosine_similarity(query_vector, vector)[0][0]
        if similarity > max_similarity:
            max_similarity = similarity
            most_similar_index = idx
    return most_similar_index


def calculate_similar(va, vb):
    va = np.array(va).reshape(1, -1)
    vb = np.array(vb).reshape(1, -1)
    _val = cosine_similarity(va, vb)[0][0]
    return _val.item()


class EmbeddingTaskClient:
    def __init__(self, url: str):
        self.url = url
        opts = common_grpc_opts
        self.channel = grpc.insecure_channel(url, options=opts)
        self.stub = EmbedStub(self.channel)
        logger.info("embedding client 初始化完成...")

    def embedding(self, text: str, max_length: int = 512) -> List[float]:
        pb2_req = EmbedRequest(input=text, max_length=max_length)
        pb2_resp: EmbedResponse = self.stub.Embed(pb2_req)
        resp = MessageToDict(pb2_resp)
        return resp["embeddings"]

    def batch_embedding(self, texts: List[str], max_length: int = 512, batch_size: int = 20) -> List[List[float]]:
        pb2_req = BatchEmbedRequest(inputs=texts, max_length=max_length, batch_size=batch_size)
        pb2_resp: BatchEmbedResponse = self.stub.BatchEmbed(pb2_req)
        resp = MessageToDict(pb2_resp)
        return [item["values"] for item in resp["embeddings"]]

    def text_similar(self, query: str, texts: List[str]) -> tuple[str, float]:
        _all = [query]
        _all.extend(texts)
        vectors = self.batch_embedding(_all)
        query_vector = vectors[0]
        texts_vector = vectors[1:]
        idx = find_most_similar_vector(query_vector, texts_vector)
        similar_score = calculate_similar(query_vector, texts_vector[idx])
        return texts[idx], similar_score

    def calculate_text_similar(self, query: str, text: str) -> float:
        _all = [query]
        _all.extend(text)
        vectors = self.batch_embedding(_all)
        query_vector = vectors[0]
        text_vector = vectors[1]
        similar_score = calculate_similar(query_vector, text_vector)
        return similar_score

    def terms_weight_analyse(self, terms: List[str]) -> List[int]:
        a = "".join(terms)
        texts = []
        for i in range(len(terms)):
            tp = terms.copy()
            tp.pop(i)
            texts.append("".join(tp))
        # embedding
        _all = [a]
        _all.extend(texts)
        vectors = self.batch_embedding(_all)
        va = vectors[0]
        texts_vector = vectors[1:]
        # calculate similar
        similars = []
        for vb in texts_vector:
            s = calculate_similar(va, vb)
            similars.append(s)
        # weight
        weights = [int(round((1 - s), 2) * 100) for s in similars]
        return weights

    def close(self):
        if self.channel:
            self.channel.close()

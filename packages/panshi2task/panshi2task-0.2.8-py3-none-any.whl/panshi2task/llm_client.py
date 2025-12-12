from typing import List, Dict

import grpc
from google.protobuf.json_format import ParseDict, MessageToDict
from loguru import logger
from pydantic import BaseModel

from panshi2task.base import common_grpc_opts
from panshi2task.grpc_gen.task_llm_pb2 import EntityMiniingRequest, EntityMiniingResponse, FAQMiniingRequest, \
    QuestionGenRequest, SummaryRequest, TopicMiningRequest, TableSummaryRequest, SummaryBatchRequest, \
    TableSummaryBatchRequest, EntityMiniingBatchRequest, EntityMiniingBatchResponse, FAQMiniingBatchRequest, \
    QuestionGenBatchRequest, TopicMiningBatchRequest, \
    QuestionGenRequest, SummaryRequest, TopicMiningRequest, TableSummaryRequest, \
    TranslateRequest, TranslateBatchRequest, GenerateCateRequest, GenerateCateBatchRequest, \
    DeriveSubCategoryRequest, AggregateSubCategoryRequest
from panshi2task.grpc_gen.task_llm_pb2_grpc import EntityMiniingStub, FAQMiniingStub, QuestionGenStub, SummaryStub, \
    TopicMiningStub, TableSummaryStub, TranslateStub, GenerateCateStub, DeriveSubCategoryStub, AggregateSubCategoryStub


class QAItem(BaseModel):
    query: str
    answer: str


class LlmTaskClient:
    def __init__(self, url: str):
        self.url = url
        opts = common_grpc_opts
        self.channel = grpc.insecure_channel(url, options=opts)
        self._entity_mining_stub = EntityMiniingStub(self.channel)
        self._faq_mining_stub = FAQMiniingStub(self.channel)
        self._question_gen_stub = QuestionGenStub(self.channel)
        self._summary_stub = SummaryStub(self.channel)
        self._table_summary_stub = TableSummaryStub(self.channel)
        self._topic_mining_stub = TopicMiningStub(self.channel)
        self._translate_stub = TranslateStub(self.channel)
        self._generate_cate_stub = GenerateCateStub(self.channel)
        self._derive_sub_category_stub = DeriveSubCategoryStub(self.channel)
        self._aggregate_sub_category_stub = AggregateSubCategoryStub(self.channel)
        logger.info("llm client 初始化完成...")

    def entity_mining(self, schema: List[Dict[str, str]], text: str, except_num: int = 3) -> Dict[str, List[str]]:
        req = ParseDict({"schema": schema, "text": text, "except_num": except_num}, EntityMiniingRequest())
        resp: EntityMiniingResponse = self._entity_mining_stub.excute(req)
        if resp.code == 200:
            data = MessageToDict(resp)["data"]
            # 去除值为空的项
            filtered_data = {key: value for key, value in data.items() if value}
            return filtered_data

        else:
            logger.error("message:{},detail:{}", resp.message, resp.detail)
            return {}

    def batch_entity_mining(self, entities: List[EntityMiniingRequest]) -> List[Dict[str, List[str]]]:
        request = EntityMiniingBatchRequest(entities=entities)
        resp: EntityMiniingBatchResponse = self._entity_mining_stub.batch(request)
        if resp.code == 200:
            result = MessageToDict(resp)["data"]
            entity_mining_result = []
            for data in result:
                if "data" in data:
                    # 去除值为空的项
                    filtered_data = {key: value for key, value in data["data"].items() if value}
                    entity_mining_result.append(filtered_data)
                else:
                    entity_mining_result.append({})
            return entity_mining_result
        else:
            logger.error("message:{},detail:{}", resp.message, resp.detail)
            return []

    def faq_mining(self, text: str, except_num: int = 3) -> List[QAItem]:
        req = ParseDict({"text": text, "except_num": except_num}, FAQMiniingRequest())
        resp = self._faq_mining_stub.excute(req)
        if resp.code == 200:
            return [QAItem.model_validate(item) for item in MessageToDict(resp)["data"]]
        else:
            logger.error("message:{},detail:{}", resp.message, resp.detail)
            return []

    def batch_faq_mining(self, faqs: List[FAQMiniingRequest]) -> List[List[QAItem]]:
        request = FAQMiniingBatchRequest(faqs=faqs)
        resp = self._faq_mining_stub.batch(request)
        if resp.code == 200:
            result = []
            for item in MessageToDict(resp)["data"]:
                qas = []
                if "data" in item:
                    qas = [QAItem.model_validate(qa) for qa in item["data"]]
                result.append(qas)
            return result
        else:
            logger.error("message:{},detail:{}", resp.message, resp.detail)
            return []

    def question_gen(self, text: str, except_num: int = 3) -> List[str]:
        req = ParseDict({"text": text, "except_num": except_num}, QuestionGenRequest())
        resp = self._question_gen_stub.excute(req)
        if resp.code == 200:
            return MessageToDict(resp)["data"]
        else:
            logger.error("message:{},detail:{}", resp.message, resp.detail)
            return []

    def batch_question_gen(self, question_gens: List[QuestionGenRequest]) -> List[List[str]]:
        request = QuestionGenBatchRequest(question_gens=question_gens)
        resp = self._question_gen_stub.batch(request)
        if resp.code == 200:
            result = []
            for item in MessageToDict(resp)["data"]:
                if "data" in item:
                    result.append(item["data"])
                else:
                    result.append([])
            return result
        else:
            logger.error("message:{},detail:{}", resp.message, resp.detail)
            return []

    def table_summary(self, text: str) -> str:
        req = TableSummaryRequest(text=text)
        resp = self._table_summary_stub.excute(req)
        if resp.code == 200:
            return resp.data
        else:
            logger.error("message:{},detail:{}", resp.message, resp.detail)
            return ""

    def batch_table_summary(self, texts: List[str]) -> List[str]:
        req = TableSummaryBatchRequest(texts=texts)
        resp = self._table_summary_stub.batch(req)
        if resp.code == 200:
            return resp.data
        else:
            logger.error("message:{},detail:{}", resp.message, resp.detail)
            return []

    def summary(self, text: str) -> str:
        req = SummaryRequest(text=text)
        resp = self._summary_stub.excute(req)
        if resp.code == 200:
            return resp.data
        else:
            logger.error("message:{},detail:{}", resp.message, resp.detail)
            return ""

    def batch_summary(self, texts: List[str]) -> List[str]:
        req = SummaryBatchRequest(texts=texts)
        resp = self._summary_stub.batch(req)
        if resp.code == 200:
            return resp.data
        else:
            logger.error("message:{},detail:{}", resp.message, resp.detail)
            return []

    def topic_mining(self, summary: str, titles: List[str] | None = None, except_num: int = 3) -> List[str]:
        req = ParseDict({"summary": summary, "titles": titles, "except_num": except_num}, TopicMiningRequest())
        resp = self._topic_mining_stub.excute(req)
        if resp.code == 200:
            return MessageToDict(resp)["data"]
        else:
            logger.error("message:{},detail:{}", resp.message, resp.detail)
            return []

    def batch_topic_mining(self, topics: List[TopicMiningRequest]) -> List[List[str]]:
        request = TopicMiningBatchRequest(topics=topics)
        resp = self._topic_mining_stub.batch(request)
        if resp.code == 200:
            result = []
            for item in MessageToDict(resp)["data"]:
                if "data" in item:
                    result.append(item["data"])
                else:
                    result.append([])
            return result
        else:
            logger.error("message:{},detail:{}", resp.message, resp.detail)
            return []

    def translate(self, to_language: str, text: str) -> str:
        req = TranslateRequest(to_language=to_language, text=text)
        resp = self._translate_stub.excute(req)
        if resp.code == 200:
            return MessageToDict(resp)["data"]
        else:
            logger.error("message:{},detail:{}", resp.message, resp.detail)
            return ""

    def translate_batch(self, to_language: str, texts: List[str]) -> List[str]:
        req = TranslateBatchRequest(to_language=to_language, text=texts)
        resp = self._translate_stub.batch(req)
        if resp.code == 200:
            return MessageToDict(resp)["data"]
        else:
            logger.error("message:{},detail:{}", resp.message, resp.detail)
            return []

    def generate_cate(self, fileid: str, filename: str, keyword: str, summary: str, cates: str) -> Dict:
        """
        调用 GenerateCate 服务执行分类生成
        """
        req = ParseDict({
            "fileid": fileid,
            "filename": filename,
            "keyword": keyword,
            "summary": summary,
            "cates": cates
        }, GenerateCateRequest())
        resp = self._generate_cate_stub.execute(req)
        if resp.fileid:
            return MessageToDict(resp)
        else:
            logger.error("message: GenerateCate failed")
            return {}

    def batch_generate_cate(self, requests: List[GenerateCateRequest]) -> List[Dict]:
        """
        批量调用 GenerateCate 服务执行分类生成
        """
        req = GenerateCateBatchRequest(generate_cate_requests=requests)
        resp = self._generate_cate_stub.batch(req)
        result = []
        for item in resp.generate_cate_responses:
            result.append(MessageToDict(item))
        return result

    def derive_sub_category(self, fileNames: str, primaryCategory: str) -> Dict[str, List[str]]:
        """
        调用 DeriveSubCategory 服务执行子类推导
        """
        req = ParseDict({
            "fileNames": fileNames,
            "primaryCategory": primaryCategory
        }, DeriveSubCategoryRequest())
        resp = self._derive_sub_category_stub.execute(req)
        if resp.code == 200:
            data = MessageToDict(resp)["data"]
            # 去除值为空的项
            filtered_data = {key: value for key, value in data.items() if value}
            return filtered_data
        else:
            logger.error("message:{},detail:{}", resp.message, resp.detail)
            return {}

    def aggregate_sub_category(self, subcategory: List[str]) -> List[str]:
        """
        调用 AggregateSubCategory 服务执行子类聚合
        """
        req = ParseDict({
            "subcategory": subcategory
        }, AggregateSubCategoryRequest())
        resp = self._aggregate_sub_category_stub.execute(req)
        if resp.code == 200:
            return resp.data
        else:
            logger.error("message:{},detail:{}", resp.message, resp.detail)
            return []

    def close(self):
        if self.channel:
            self.channel.close()
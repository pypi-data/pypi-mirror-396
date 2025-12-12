from typing import Iterable, List, Dict

from panshi2task.base import GrpcServerInfo, DPLUS_3_4_GRPC_SERVER
from panshi2task.embedding_client import EmbeddingTaskClient
from panshi2task.grpc_gen.task_llm_pb2 import EntityMiniingRequest, FAQMiniingRequest, QuestionGenRequest, \
    TopicMiningRequest, GenerateCateRequest, DeriveSubCategoryRequest, AggregateSubCategoryRequest
from panshi2task.llm_client import LlmTaskClient, QAItem
from panshi2task.paddle_client import PaddleTaskClient, OcrPageResult, BoxRecItem
from panshi2task.rerank_client import RerankTaskClient, RankItem
from panshi2task.torch_client import TorchTaskClient


class PanshiTaskClient:
    def __init__(self, server_info: GrpcServerInfo):
        if server_info.llm_server_url:
            self.llm_client = LlmTaskClient(server_info.llm_server_url)
        if server_info.paddle_server_url:
            self.paddle_client = PaddleTaskClient(server_info.paddle_server_url)
        if server_info.torch_server_url:
            self.torch_client = TorchTaskClient(server_info.torch_server_url)
        if server_info.embedding_server_url:
            self.embedding_client = EmbeddingTaskClient(server_info.embedding_server_url)
        if server_info.rerank_server_url:
            self.rerank_client = RerankTaskClient(server_info.rerank_server_url)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        if self.llm_client:
            self.llm_client.close()
        if self.paddle_client:
            self.paddle_client.close()
        if self.torch_client:
            self.torch_client.close()
        if self.embedding_client:
            self.embedding_client.close()
        if self.rerank_client:
            self.rerank_client.close()

    # ========================llm====================
    def entity_mining(self, schema: List[Dict[str, str]], text: str, except_num: int) -> Dict[str, List[str]]:
        assert self.llm_client is not None, "请提供llm_server_url地址"
        return self.llm_client.entity_mining(schema, text, except_num)

    def batch_entity_mining(self, entities: List[EntityMiniingRequest]) -> List[Dict[str, List[str]]]:
        assert self.llm_client is not None, "请提供llm_server_url地址"
        return self.llm_client.batch_entity_mining(entities)

    def faq_mining(self, text: str, except_num=3) -> List[QAItem]:
        assert self.llm_client is not None, "请提供llm_server_url地址"
        return self.llm_client.faq_mining(text, except_num)

    def batch_faq_mining(self, faqs: List[FAQMiniingRequest]) -> List[List[QAItem]]:
        assert self.llm_client is not None, "请提供llm_server_url地址"
        return self.llm_client.batch_faq_mining(faqs)

    def question_gen(self, text: str, except_num=3) -> List[str]:
        assert self.llm_client is not None, "请提供llm_server_url地址"
        return self.llm_client.question_gen(text, except_num)

    def batch_question_gen(self, question_gens: List[QuestionGenRequest]) -> List[List[str]]:
        assert self.llm_client is not None, "请提供llm_server_url地址"
        return self.llm_client.batch_question_gen(question_gens=question_gens)

    def summary(self, text: str) -> str:
        assert self.llm_client is not None, "请提供llm_server_url地址"
        return self.llm_client.summary(text)

    def batch_summary(self, texts: List[str]) -> List[str]:
        assert self.llm_client is not None, "请提供llm_server_url地址"
        return self.llm_client.batch_summary(texts)

    def table_summary(self, table_html: str) -> str:
        assert self.llm_client is not None, "请提供llm_server_url地址"
        return self.llm_client.table_summary(table_html)

    def batch_table_summary(self, table_htmls: List[str]) -> List[str]:
        assert self.llm_client is not None, "请提供llm_server_url地址"
        return self.llm_client.batch_table_summary(table_htmls)

    def topic_mining(self, summary: str, titles: List[str] | None = None, except_num: int = 3) -> List[str]:
        assert self.llm_client is not None, "请提供llm_server_url地址"
        return self.llm_client.topic_mining(summary, titles, except_num)

    def batch_topic_mining(self, topics: List[TopicMiningRequest]) -> List[List[str]]:
        assert self.llm_client is not None, "请提供llm_server_url地址"
        return self.llm_client.batch_topic_mining(topics)

    def translate(self, to_language: str, text: str) -> str:
        assert self.llm_client is not None, "请提供llm_server_url地址"
        return self.llm_client.translate(to_language, text)

    def translate_batch(self, to_language: str, texts: List[str]) -> List[str]:
        assert self.llm_client is not None, "请提供llm_server_url地址"
        return self.llm_client.translate_batch(to_language, texts)

    def generate_cate(self, fileid: str, filename: str, keyword: str, summary: str, cates: str) -> Dict:
        """
        调用 GenerateCate 服务执行分类生成
        """
        assert self.llm_client is not None, "请提供llm_server_url地址"
        return self.llm_client.generate_cate(fileid, filename, keyword, summary, cates)

    def batch_generate_cate(self, requests: List[GenerateCateRequest]) -> List[Dict]:
        """
        批量调用 GenerateCate 服务执行分类生成
        """
        assert self.llm_client is not None, "请提供llm_server_url地址"
        return self.llm_client.batch_generate_cate(requests)

    def derive_sub_category(self, fileNames: str, primaryCategory: str) -> Dict[str, List[str]]:
        """
        调用 DeriveSubCategory 服务执行子类推导
        """
        assert self.llm_client is not None, "请提供llm_server_url地址"
        return self.llm_client.derive_sub_category(fileNames, primaryCategory)

    def aggregate_sub_category(self, subcategory: List[str]) -> List[str]:
        """
        调用 AggregateSubCategory 服务执行子类聚合
        """
        assert self.llm_client is not None, "请提供llm_server_url地址"
        return self.llm_client.aggregate_sub_category(subcategory)

    # ========================paddle====================
    def image_ocr(self, file_path: str, file_name: str | None = None) -> OcrPageResult:
        assert self.paddle_client is not None, "请提供paddle_server_url地址"
        return self.paddle_client.image_ocr(file_path, file_name)

    def image_ocr_bytes(self, local_file_path: str) -> OcrPageResult:
        assert self.paddle_client is not None, "请提供paddle_server_url地址"
        return self.paddle_client.image_ocr_bytes(local_file_path)

    def pdf_ocr(self, file_path: str, file_name: str | None = None) -> Iterable[OcrPageResult]:
        assert self.paddle_client is not None, "请提供paddle_server_url地址"
        return self.paddle_client.pdf_ocr(file_path, file_name)

    def pdf_ocr_bytes(self, local_file_path: str) -> Iterable[OcrPageResult]:
        assert self.paddle_client is not None, "请提供paddle_server_url地址"
        return self.paddle_client.pdf_ocr_bytes(local_file_path)

    def pdf_structure(self, file_path: str, file_name: str | None = None) -> Iterable[BoxRecItem]:
        assert self.paddle_client is not None, "请提供paddle_server_url地址"
        return self.paddle_client.pdf_structure(file_path, file_name)

    def pdf_structure_bytes(self, local_file_path: str) -> Iterable[BoxRecItem]:
        assert self.paddle_client is not None, "请提供paddle_server_url地址"
        return self.paddle_client.pdf_structure_bytes(local_file_path)

    def entity_extract(self, schema: List[str], inputs: List[str]) -> List[Dict]:
        assert self.paddle_client is not None, "请提供paddle_server_url地址"
        return self.paddle_client.entity_extract(schema, inputs)

    def relation_extract(self, schema: Dict, inputs: List[str]) -> List[Dict]:
        assert self.paddle_client is not None, "请提供paddle_server_url地址"
        return self.paddle_client.relation_extract(schema, inputs)

    # ========================torch====================
    def text_error_correction(self, texts: List[str]) -> List[str]:
        assert self.torch_client is not None, "请提供torch_server_url地址"
        return self.torch_client.text_error_correction(texts)

    def doc_seg(self, text: str) -> List[str]:
        assert self.torch_client is not None, "请提供torch_server_url地址"
        return self.torch_client.doc_seg(text)

    # ========================embedding====================
    def embedding(self, text: str, max_length: int = 512) -> List[float]:
        assert self.embedding_client is not None, "请提供embedding_server_url地址"
        return self.embedding_client.embedding(text, max_length)

    def batch_embedding(self, texts: List[str], max_length: int = 512, batch_size: int = 20) -> List[List[float]]:
        assert self.embedding_client is not None, "请提供embedding_server_url地址"
        return self.embedding_client.batch_embedding(texts, max_length, batch_size)

    def text_similar(self, query, texts: List[str]) -> str:
        assert self.embedding_client is not None, "请提供embedding_server_url地址"
        return self.embedding_client.text_similar(query, texts)

    def calculate_text_similar(self, query: str, text: str) -> float:
        assert self.embedding_client is not None, "请提供embedding_server_url地址"
        return self.embedding_client.calculate_text_similar(query, text)

    def terms_weight_analyse(self, terms: List[str]) -> List[int]:
        assert self.embedding_client is not None, "请提供embedding_server_url地址"
        return self.embedding_client.terms_weight_analyse(terms)

    # ========================rerank====================
    def rerank(self, query: str, texts: List[str], truncate: bool = True, raw_scores: bool = False,
               return_text: bool = True) -> List[RankItem]:
        assert self.rerank_client is not None, "请提供rerank_server_url地址"
        return self.rerank_client.rerank(query, texts, truncate, raw_scores, return_text)


if __name__ == '__main__':
    with PanshiTaskClient(DPLUS_3_4_GRPC_SERVER) as client:
        s = "asdad"
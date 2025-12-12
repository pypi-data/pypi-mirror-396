from enum import Enum

from grpc._cython import cygrpc
from pydantic import BaseModel

common_grpc_opts = [
    (cygrpc.ChannelArgKey.max_send_message_length, -1),
    (cygrpc.ChannelArgKey.max_receive_message_length, -1),
    ("grpc.enable_retries", 1),
    ("grpc.keepalive_time_ms", 55000),
]


class GrpcServerInfo(BaseModel):
    llm_server_url: str | None = None
    paddle_server_url: str | None = None
    torch_server_url: str | None = None
    embedding_server_url: str | None = None
    rerank_server_url: str | None = None


DPLUS_3_4_IP = "192.168.3.4"
DPLUS_3_4_GRPC_SERVER = GrpcServerInfo(
    llm_server_url=f"{DPLUS_3_4_IP}:8011",
    paddle_server_url=f"{DPLUS_3_4_IP}:8012",
    torch_server_url=f"{DPLUS_3_4_IP}:8013",
    embedding_server_url=f"{DPLUS_3_4_IP}:18006",
    rerank_server_url=f"{DPLUS_3_4_IP}:18007"
)

DPLUS_3_10_IP = "192.168.3.10"
DPLUS_3_10_GRPC_SERVER = GrpcServerInfo(
    llm_server_url=f"{DPLUS_3_10_IP}:8011",
    paddle_server_url=f"{DPLUS_3_10_IP}:8012",
    torch_server_url=f"{DPLUS_3_10_IP}:8013",
    embedding_server_url=f"{DPLUS_3_10_IP}:18006",
    rerank_server_url=f"{DPLUS_3_10_IP}:18007"
)

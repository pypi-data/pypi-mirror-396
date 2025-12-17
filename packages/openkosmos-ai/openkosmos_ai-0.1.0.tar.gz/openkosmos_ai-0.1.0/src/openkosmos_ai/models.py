from typing import Optional

from pydantic import BaseModel


class VectorStoreConfig(BaseModel):
    model: str
    index_dir: Optional[str] = None
    index_name: Optional[str] = None
    top_k: Optional[int] = 3


class RAGFlowServerConfig(BaseModel):
    base_url: str
    api_key: str


class XinferenceServerConfig(BaseModel):
    base_url: str
    api_key: str
    mode: Optional[str] = "http"
    rerank_model: Optional[str] = "bge-reranker-v2-m3"
    embed_model: Optional[str] = "bge-m3"


class DatabaseServerConfig(BaseModel):
    url: str


class DifyServerConfig(BaseModel):
    name: str
    url: str
    email: str
    password: str


class OpenAIServerConfig(BaseModel):
    base_url: str
    api_key: str
    model: Optional[str] = None


class GitRepoConfig(BaseModel):
    repo_dir: str
    remote_branch: str
    remote_url: str
    username: str
    email: str

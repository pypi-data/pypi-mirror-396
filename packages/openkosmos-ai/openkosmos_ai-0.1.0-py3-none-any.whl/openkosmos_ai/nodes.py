import os
from typing import Optional, List
from uuid import uuid4

import faiss
import requests
from git import Repo
from langchain_community.docstore import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, SecretStr
from ragflow_sdk import RAGFlow
from sqlalchemy import create_engine

from openkosmos_ai.models import VectorStoreConfig, XinferenceServerConfig, DatabaseServerConfig, \
    RAGFlowServerConfig, DifyServerConfig, GitRepoConfig, OpenAIServerConfig


class SearchResult(BaseModel):
    similarity_score: float
    relevance_score: Optional[float] = 0
    doc: dict


class VectorStoreNode:
    def __init__(self, store_config: VectorStoreConfig):
        self.store_config = store_config
        self.vector_store = None
        self.embedding_model = HuggingFaceEmbeddings(model_name=self.store_config.model,
                                                     model_kwargs={'device': 'cpu'})

    def store(self):
        return self.vector_store

    def load_index(self):
        self.vector_store = FAISS.load_local(folder_path=self.store_config.index_dir,
                                             index_name=self.store_config.index_name,
                                             embeddings=self.embedding_model,
                                             allow_dangerous_deserialization=True,
                                             normalize_L2=True)

    def build_index(self, documents: list[Document]):
        self.vector_store = FAISS(
            embedding_function=self.embedding_model,
            index=faiss.IndexFlatIP(len(self.embedding_model.embed_query("AI"))),
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
            normalize_L2=True
        )

        self.vector_store.add_documents(documents=documents,
                                        ids=[str(uuid4()) for _ in range(len(documents))])
        if self.store_config.index_name is not None and self.store_config.index_dir is not None:
            self.vector_store.save_local(folder_path=self.store_config.index_dir,
                                         index_name=self.store_config.index_name)

    def search(self, query: str, threshold=0.8, filter_meta={}) -> list[SearchResult]:
        results = self.vector_store.similarity_search_with_score(query=query, k=self.store_config.top_k,
                                                                 filter=filter_meta)
        return [SearchResult(similarity_score=score, doc=doc.model_dump())
                for doc, score in results if score > threshold]


class XinferenceClientNode:
    def __init__(self, server_config: XinferenceServerConfig):
        self.server_config = server_config
        # if server_config.mode == "client":
        #     self.client = RESTfulClient(server_config.base_url)
        #     self.rerank_model: RESTfulRerankModelHandle = self.client.get_model("bge-reranker-v2-m3")
        #     self.embed_model: RESTfulEmbeddingModelHandle = self.client.get_model("bge-m3")

    def client(self):
        if self.server_config.mode == "http":
            return None
        # else:
        #     return self.client

    def rerank(self, documents: List[str], query: str, top_n=3):
        if self.server_config.mode == "http":
            return requests.post(self.server_config.base_url + "/v1/rerank",
                                 json={
                                     "model": self.server_config.rerank_model,
                                     "query": query,
                                     "documents": documents,
                                     "top_n": top_n
                                 }).json()["results"]
        # else:
        #     return self.rerank_model.rerank(documents=documents, query=query, top_n=top_n)["results"]

    def embed(self, input: str):
        if self.server_config.mode == "client":
            return requests.post(self.server_config.base_url + "/v1/embeddings",
                                 json={
                                     "model": self.server_config.embed_model,
                                     "input": input,
                                     "encoding_format": "float"
                                 }).json()
        # else:
        #     return self.embed_model.create_embedding(input)


class DatabaseClientNode:
    def __init__(self, server_config: DatabaseServerConfig):
        self.database_engine = create_engine(server_config.url, pool_size=10)

    def engine(self):
        return self.database_engine


class RAGFlowClientNode:
    def __init__(self, server_config: RAGFlowServerConfig):
        self.server_config = server_config
        self.ragflow_client = RAGFlow(
            base_url=server_config.base_url,
            api_key=server_config.api_key
        )
        self.auth_header = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {server_config.api_key}"
        }

    def client(self):
        return self.ragflow_client

    def list_datasets(self, page=1, page_size=1000, id=None):
        return self.ragflow_client.list_datasets(page=page, page_size=page_size, id=id)

    def get_document_chunks(self, dataset_id: str, document_id: str, page=1, page_size=1000):
        return requests.get(self.server_config.base_url +
                            f"/datasets/{dataset_id}/documents/{document_id}/chunks?page={page}&page_size={page_size}",
                            headers=self.auth_header).json()

    def get_documents(self, dataset_id: str, document_id: str = None, page=1, page_size=1000):
        return requests.get(self.server_config.base_url +
                            f"/datasets/{dataset_id}/documents?page={page}&page_size={page_size}" + (
                                "" if document_id is None else f"&id={document_id}"),
                            headers=self.auth_header).json()

    def get_document_content(self, dataset_id: str, document_id: str):
        return requests.get(self.server_config.base_url +
                            f"/datasets/{dataset_id}/documents/{document_id}",
                            headers=self.auth_header).content

    def retrieve(self, question: str, dataset_ids: list[str], top_k=1):
        return [c.to_json() for c in self.ragflow_client.retrieve(
            question=question,
            dataset_ids=dataset_ids,
            top_k=top_k)]


class DifyClientNode:
    def __init__(self, server_config: DifyServerConfig):
        self.server_config = server_config
        access_token = DifyClientNode.login(server_config)

        self.auth_header = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }

    def config(self) -> DifyServerConfig:
        return self.server_config

    @staticmethod
    def login(server_config: DifyServerConfig):
        return requests.post(server_config.url + "/console/api/login", json={
            "email": server_config.email,
            "password": server_config.password,
            "language": "zh-Hans",
            "remember_me": "true"
        }).json()["data"]["access_token"]

    def console_api_apps(self, page=1, limit=100):
        return requests.get(self.server_config.url + f"/console/api/apps?page={page}&limit={limit}",
                            headers=self.auth_header).json()

    def console_api_apps_export(self, app_id: str):
        return requests.get(self.server_config.url + f"/console/api/apps/{app_id}/export?include_secret=true",
                            headers=self.auth_header).json()


class GitRepoNode:
    def __init__(self, repo_config: GitRepoConfig):
        self.repo_config = repo_config
        self.git_repo = GitRepoNode.init_repo(repo_config)

    def config(self) -> GitRepoConfig:
        return self.repo_config

    def repo(self) -> Repo:
        return self.git_repo

    def commit(self, commit_message: str):
        modified_files = [item.a_path for item in self.repo().index.diff(None)]
        changed_files = self.repo().untracked_files + modified_files

        self.repo().index.add(changed_files)

        if len(changed_files) > 0:
            self.repo().index.commit(commit_message)

        return changed_files

    def push(self, close=True):
        origin = self.repo().remote(name="origin")
        origin.push()

        if close:
            self.repo().close()

    def close(self):
        self.repo().close()

    @staticmethod
    def init_repo(repo_config: GitRepoConfig):
        if os.path.exists(repo_config.repo_dir):
            repo = Repo(repo_config.repo_dir)
        else:
            repo = Repo.clone_from(repo_config.remote_url, repo_config.repo_dir)
            repo.git.config("user.name", repo_config.username)
            repo.git.config("user.email", repo_config.email)
            repo.git.checkout("-b", repo_config.remote_branch, f"origin/{repo_config.remote_branch}")

        return repo


class OpenAIChatNode:
    def __init__(self, server_config: OpenAIServerConfig, temperature=0.7, top_p=0.8,
                 presence_penalty=1.03):
        self.llm = ChatOpenAI(
            model=server_config.model,
            base_url=server_config.base_url,
            api_key=SecretStr(server_config.api_key),
            temperature=temperature,
            top_p=top_p,
            presence_penalty=presence_penalty
        )

    def model(self):
        return self.llm

    def invoke(self, messages):
        response = self.llm.invoke(messages)
        return response

    def chat(self, messages):
        response = self.llm.invoke(messages)
        return response.content_blocks


class NoOperationNode:
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        pass

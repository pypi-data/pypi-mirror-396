from typing import Optional

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, SecretStr


class OpenAIServerConfig(BaseModel):
    base_url: str
    api_key: str
    model: Optional[str] = None


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

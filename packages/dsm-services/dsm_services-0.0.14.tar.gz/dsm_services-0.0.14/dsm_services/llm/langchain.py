from typing import Optional
from langchain_core.language_models import BaseChatModel
from langchain.schema import (
    AIMessage,
    BaseMessage,
    ChatGeneration,
    ChatResult,
)
from . import base
from dsm_services import utils

def langchain2ollama(msg):
    roles = {
        'human': 'user',
        'ai': 'assistant',
        'system': 'system'
    }
    return {
        'role': roles.get(getattr(msg, 'type')),
        'content': getattr(msg, 'content')
    }

class llmChatModel(BaseChatModel):
    model_name: str = "llama3.1"
    api_key: str
    llm_uri: Optional[str]
    llm: object = None

    def __init__(self, model_name, api_key, llm_uri=None, _llm=None):
        _params = {
            'model_name': model_name,
            'api_key': api_key,
        }
        if llm_uri != None: _params.update({'llm_uri': llm_uri})
        super().__init__(**_params)
        self.llm = base.LLM(**_params)

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list = None
    ) -> ChatResult:
        """
        Generate a response from the Ollama model based on a list of messages.
        """

        _msg = [langchain2ollama(elm) for elm in messages]


        res = self.llm.chat(messages=_msg)
        ai_message = AIMessage(content=res.message.get('content'))
        return ChatResult(generations=[ChatGeneration(message=ai_message)])

    @property
    def _identifying_params(self) -> dict:
        """
        Return identifying parameters for the model.
        """
        return {"model": self.model_name}

    @property
    def _llm_type(self) -> str:
        return f"ollama: {self.model_name}"
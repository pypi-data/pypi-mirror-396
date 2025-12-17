import requests
from dsm_services import utils

class llmResponse:
    def __init__(self, data):
        self.data = data
        for k,v in data.items():
            setattr(self, k, v)
    def __repr__(self):
        text = str(getattr(self, 'response') or getattr(self, 'messages') or getattr(self, 'embeddings'))
        return f"llmResponse (response: {text[:100]}...)"
    
class LLM:
    def __init__(self, model_name, api_key, llm_uri="https://llm.services.storemesh.com"):
        self.headers = {
            'Authorization': f"Api-Key {api_key}"
        }
        self.uri = llm_uri
        self.model_name = model_name
        self.api_key = api_key

        self._init()

    def __repr__(self):
        prefix, suffix = self.api_key.split('.')
        return f"LLM (model {self.model_name}) (key:{prefix}.{'*'*len(suffix)})"

    def _init(self):
        res = requests.get(f"{self.uri}/llm/api/llm/", headers=self.headers)
        utils.check_http_status_code(response=res, extra_text="inllmChatModelit fail")
        if self.model_name not in [elm.get('name') for elm in res.json()]:
            raise Exception(f"`{self.model_name}` not avalible for key `{self.api_key}`")
        try: self.generate_content(prompt="Hi")
        except Exception: raise Exception(f"init model {self.model_name} fail!")

    def generate_content(self, prompt):
        res = requests.post(
            f"{self.uri}/llm/api/llm/{self.model_name}/generate/", 
            headers=self.headers,
            json={
                'prompt': prompt
            }
        )
        utils.check_http_status_code(response=res, extra_text="generate_content ")
        return llmResponse(res.json())
    
    def chat(self, messages):
        res = requests.post(
            f"{self.uri}/llm/api/llm/{self.model_name}/chat/", 
            headers=self.headers,
            json={
                'messages': messages
            }
        )
        utils.check_http_status_code(response=res, extra_text="chat ")
        return llmResponse(res.json())
    
    def embed(self, texts):
        res = requests.post(
            f"{self.uri}/llm/api/llm/{self.model_name}/embed/", 
            headers=self.headers,
            json={
                'texts': texts
            }
        )
        utils.check_http_status_code(response=res, extra_text="embed ")
        return llmResponse(res.json())
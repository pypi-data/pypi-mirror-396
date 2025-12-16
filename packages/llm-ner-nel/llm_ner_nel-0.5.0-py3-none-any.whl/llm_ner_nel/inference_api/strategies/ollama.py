import logging
from typing import Type
from llm_ner_nel.inference_api.llm_config import LlmConfig
from ollama import Client

from llm_ner_nel.inference_api.strategies.base import T, LLMProviderStrategy

class OllamaStrategy(LLMProviderStrategy):
    def __init__(self, host: str, llm_config: LlmConfig):
        self.client = Client(host=host)
        self.llm_config = llm_config

    def inference(self, prompt: str, system: str, model: str, json_response_type: Type[T]) -> T:
        options = {
            "top_k": self.llm_config.top_k,
            "top_p": self.llm_config.top_p,
            "max_tokens": self.llm_config.max_tokens,
            "temperature": self.llm_config.temperature,
            "repeat_penalty": self.llm_config.repeat_penalty,
            "frequency_penalty": self.llm_config.frequency_penalty,
            "typical_p": self.llm_config.typical_p,
            "num_thread": self.llm_config.num_thread,
        }
        
        logging.info(f"Ollama host: {self.client._client.base_url}")

        response = self.client.generate(
            prompt=prompt,
            system=system,
            model=model,
            format=json_response_type.model_json_schema(),
            options=options
        )
        return json_response_type.model_validate_json(response.response)
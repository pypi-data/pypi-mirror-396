import logging
from typing import Type
from llm_ner_nel.inference_api.llm_config import LlmConfig
from ollama import Client

from llm_ner_nel.inference_api.strategies.base import T, LLMProviderStrategy

class OllamaSlimStrategy(LLMProviderStrategy):
    def __init__(self, host: str, llm_config: LlmConfig):
        self.client = Client(host=host)
        self.llm_config = llm_config

    def inference(self, prompt: str, system: str, model: str, json_response_type: Type[T]) -> T:
        options = {
            "temperature": self.llm_config.temperature,
            "num_thread": self.llm_config.num_thread,
        }
        
        single_user_prompt = self.create_single_prompt(prompt= prompt, system=system, json_response_type=json_response_type)
        
        logging.info(f"Ollama host (slim): {self.client._client.base_url}")

        response = self.client.generate(
            prompt=single_user_prompt,
            model=model,
            options=options
        )
        
        json = self.parse_json_block(response.response)
        return json_response_type.model_validate_json(json)
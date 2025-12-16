import logging
from typing import Type
from llm_ner_nel.inference_api.llm_config import LlmConfig
from openai import OpenAI

from llm_ner_nel.inference_api.strategies.base import T, LLMProviderStrategy

class GptOssStrategy(LLMProviderStrategy):
    def __init__(self, host="http://localhost:11434/v1", llm_config = LlmConfig()):
        self.llm_config = llm_config
        self.client = OpenAI(
            base_url=host,
            # Dummy key
            api_key="ollama")                    
 


    def inference(self, prompt: str, system: str, model: str, json_response_type: Type[T]) -> T:
        logging.info(f"Ollama host using GPT-OSS with OpenAI Client: {self.client._client.base_url}")
        
        single_user_prompt = self.create_single_prompt(prompt= prompt, system=system, json_response_type=json_response_type)
            
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": single_user_prompt}
            ],
            temperature=self.llm_config.temperature)
        
        
        result_str = response.choices[0].message.content
        
        if result_str is None:
            raise ValueError("GPT-OSS Empty response")
        
        return json_response_type.model_validate_json(self.parse_json_block(result_str))
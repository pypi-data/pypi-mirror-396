import os
from google import genai
from typing import Optional, Type
from llm_ner_nel.inference_api.strategies.base import T, LLMProviderStrategy


class GoogleStrategy(LLMProviderStrategy):
    def __init__(self, api_key: Optional[str] = None):
        
        key = api_key or os.environ.get("GEMINI_API_KEY")
        if not key:
             raise ValueError("Missing GEMINIE_API_KEY environment variable")
        self.client = genai.Client(api_key=key)

    def inference(self, prompt: str, system: str, model: str, json_response_type: Type[T]) -> T:
        single_user_prompt = self.create_single_prompt(prompt= prompt, system=system, json_response_type=json_response_type)
        
        response = self.client.models.generate_content(
            model=model,
            contents=single_user_prompt)
        
        return json_response_type.model_validate_json(self.parse_json_block(response.text))
        
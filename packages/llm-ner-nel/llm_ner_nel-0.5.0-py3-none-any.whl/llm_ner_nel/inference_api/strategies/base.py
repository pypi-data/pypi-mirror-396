from abc import ABC, abstractmethod
import re
from typing import Type, TypeVar
from tenacity import retry, wait_exponential, stop_after_attempt

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class LLMProviderStrategy(ABC):
    @retry(
        wait=wait_exponential(multiplier=4, min=3, max=36),
        stop=stop_after_attempt(5))
    @abstractmethod
    def inference(self, prompt: str, system: str, model: str, json_response_type: Type[T]) -> T:
        pass
    
    def parse_json_block(self, response:str | None) -> str:
        pattern = r"```json(.*?)```"
        
        if response is None:
            raise ValueError("API returned empty content")
        
        match = re.search(pattern=pattern, string=response, flags=re.DOTALL | re.IGNORECASE)
        
        if not match:
            raise ValueError("No JSON code block found.")
        
        json = match.group(1).strip()
        
        if not json:
            raise ValueError("Json code block empty")
        
        return json
    
    def create_single_prompt(self, prompt:str, system:str, json_response_type: Type[T]):
        return f"""{system}. {prompt}. Return ONLY valid JSON and wrap it in a code block like this:

            ```json
            {{
                "Value":"Response",
                "Value":"Response",
            }}. 
            
            Json schema: {json_response_type.model_json_schema()}"""














            
        
    


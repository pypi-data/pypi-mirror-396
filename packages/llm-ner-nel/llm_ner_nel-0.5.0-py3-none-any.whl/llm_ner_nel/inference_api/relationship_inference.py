from llm_ner_nel.core.dto import Relationships
from llm_ner_nel.inference_api.mlflow_config import MlFlowConfig
from llm_ner_nel.inference_api.prompts import default_knowledge_graph_user_prompt, default_knowledge_graph_system_prompt
from llm_ner_nel.inference_api.llm_config import LlmConfig
from llm_ner_nel.inference_api.strategies.strategy_factory import create_inference_strategy_local
import logging
import mlflow
from mlflow import genai


def display_relationships(relationships : Relationships, console_log: bool = True) -> None:
    logging.info(relationships.topic)
    for rel in relationships.relationships:
        message = f"{rel.head}:({rel.head_confidence}) ({rel.head_type}) --[{rel.relation}]-> {rel.tail}:({rel.tail_confidence}) ({rel.tail_type})"
        if(console_log):
            print(message)
        logging.info(message)
        

class RelationshipInferenceProvider:
    model: str
    strategy: str
    mlflow_config: MlFlowConfig
    
    
    
    def __init__(self, **kwargs):
        self.model = kwargs.get('model', "llama3.2")
        self.llm_config = LlmConfig(
                       temperature = 0.5,
                       top_p = 0.3,
                       typical_p = 0.9,
                       top_k = 50,
                       max_tokens = 256,
                       repeat_penalty = 1.2,
                       frequency_penalty = 0.1,
                       presence_penalty = 0.1,
                       num_thread = 16
                       )
        
        self.mlflow_config =  kwargs.get('mlflow_config', MlFlowConfig())
        
        self.inference_strategy = create_inference_strategy_local(
            name=kwargs.get('strategy', "ollama"), 
            llm_config=self.llm_config)
        
        mlflow.set_tracking_uri(self.mlflow_config.tracking_host)

    def inference(self, prompt: str, system: str) -> Relationships:
        return self.inference_strategy.inference(prompt=prompt, system=system, model=self.model, json_response_type=Relationships)

    def generate_prompt(self, text) -> str:
        if(self.mlflow_config.mlflow_user_prompt_id is None):
            return default_knowledge_graph_user_prompt(text=text)
                    
        return str(genai.load_prompt(f"prompts:/{self.mlflow_config.mlflow_user_prompt_id}").format(text=text))
    
    def generate_system_prompt(self) -> str:
        if(self.mlflow_config.mlflow_system_prompt_id is None):
            return default_knowledge_graph_system_prompt
        
        return str(genai.load_prompt(f"prompts:/{self.mlflow_config.mlflow_system_prompt_id}").format())

    def get_relationships(self, text: str) -> Relationships:
        cleaned = text
        prompt = self.generate_prompt(cleaned)
        system_prompt = self.generate_system_prompt();

        return self.inference(
            prompt=prompt,
            system=system_prompt)
        

    

    

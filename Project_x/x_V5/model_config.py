# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from tools_handling import tool_call
from dataclasses import dataclass
from dotenv import load_dotenv
from enum import Enum
import os

load_dotenv()


#model configuration

#Enum
class ModelTier(Enum):
    fast = "Fast"
    smart = "Smart"
    
    
@dataclass
class ModelConfig:
    model_name: str
    temperature: float
    max_tokens: int = 4096
    
MODEL_MAP = {
    ModelTier.fast: ModelConfig(
        model_name= "gemini 2.5 Flash",
        temperature= 0.6,
        # max_tokens=4096
        
    ),
    ModelTier.smart: ModelConfig(
        model_name= "openai/gpt-oss-120b",
        temperature= 1.0,
        # max_tokens=4096
    ),
    
    # ModelTier.classifier: ModelConfig(
    #     model_name="llama-3.2-3b-preview",
    #     temperature= 0.0,   
    # )
}

# def get_tools():
#     global  catched_tools
#     if catched_tools is None:
#         catched_tools = tool_call()
#     return catched_tools
    


def log_routing_decision(decision: dict) -> ModelConfig:
    """
    Routing stats and returns model config
    """
    category = decision["category"]
    confidence = decision["confidence"]
    model_tier_str = decision.get["model"]
    tools = decision["tool"]
    
    try:
        tier = ModelTier(model_tier_str)
    except ValueError:
        raise ValueError(f"unkown model tier '{model_tier_str}' for intent '{category}'")
    
    config = MODEL_MAP[tier]
    
    print(f"-----[Routing Decision]-----")
    print(f"Intent detected : {category}")
    print(f"Confidence      : {confidence}")
    print(f"Model tier      : {tier.value}")
    print(f"Model ID        : {config.model_name}")
    print(f"Tools           : {tools}")
    
    return tier


def endpoint(config):
    if ModelTier.fast:
        gemini_model = ChatOpenAI(
            model=config.model_name,
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/" ,
            temperature=config.temperature
        )
        return gemini_model
        # i want to put here where it fallback to smaller llm if above fails
    
    if ModelTier.smart:
        groq_model = ChatOpenAI(
            model=config.model_name,
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
            temperature=config.temperature
        )
        return groq_model
    # if this model fail flalback to fast 
     
    
CLASSIFIER_CONFIG = ModelConfig(
    model_name="llama-3.2-3b-preview",
    temperature=0.0
)
 
def classifier_endpoint():
    classifier_model = ChatOpenAI(
        model=CLASSIFIER_CONFIG.model_name,
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1",
        temperature=CLASSIFIER_CONFIG.temperature
    )
    return classifier_model

        
        

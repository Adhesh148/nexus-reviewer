from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel
from config.config import config
from openai import OpenAI

def create_chat_model() -> BaseChatModel:
    # Create gpt-4o-mini as the default chat model -- configure its properties
    model_id = "gpt-4o-mini"
    max_tokens = 4096

    return ChatOpenAI(
        model=model_id,
        temperature=0,
        max_tokens=max_tokens,
        timeout=300,
        max_retries=2,
        api_key=config.OPENAI_API_KEY,
    )
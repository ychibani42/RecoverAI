from functools import lru_cache

from langchain_anthropic import ChatAnthropic

from recovery_ia.config import get_settings


@lru_cache
def get_llm() -> ChatAnthropic:
    settings = get_settings()
    return ChatAnthropic(model=settings.llm_model, api_key=settings.anthropic_api_key)

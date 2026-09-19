from functools import lru_cache

from langchain_nebius import ChatNebius

from recovery_ia.config import get_settings


@lru_cache
def get_llm() -> ChatNebius:
    settings = get_settings()
    return ChatNebius(model=settings.llm_model, api_key=settings.nebius_api_key)

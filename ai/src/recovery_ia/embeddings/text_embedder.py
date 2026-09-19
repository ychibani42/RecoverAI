from functools import lru_cache

from langchain_nebius import NebiusEmbeddings

from recovery_ia.config import get_settings


@lru_cache
def get_text_embedder() -> NebiusEmbeddings:
    """Embedder de texto para las notas diagnosticas/seguimiento.

    Usa un modelo multilingue (Qwen3 Embedding) via la API de Nebius.
    """
    settings = get_settings()
    return NebiusEmbeddings(model=settings.text_embedding_model, api_key=settings.nebius_api_key)

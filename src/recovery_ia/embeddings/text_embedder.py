from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings

from recovery_ia.config import get_settings


@lru_cache
def get_text_embedder() -> HuggingFaceEmbeddings:
    """Embedder de texto para las notas diagnosticas/seguimiento.

    Usa un modelo multilingue por defecto ya que las notas se generan en espanol.
    """
    settings = get_settings()
    return HuggingFaceEmbeddings(model_name=settings.text_embedding_model)

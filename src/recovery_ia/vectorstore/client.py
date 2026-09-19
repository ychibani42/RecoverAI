from functools import lru_cache

from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from recovery_ia.config import get_settings
from recovery_ia.embeddings import get_text_embedder


@lru_cache
def get_qdrant_client() -> QdrantClient:
    settings = get_settings()
    return QdrantClient(url=settings.qdrant_url)


def ensure_collection(vector_size: int) -> None:
    """Crea la coleccion en Qdrant si no existe todavia."""
    settings = get_settings()
    client = get_qdrant_client()
    if not client.collection_exists(settings.qdrant_collection):
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )


@lru_cache
def get_vectorstore() -> QdrantVectorStore:
    """Vector store de LangChain sobre Qdrant, listo para similarity_search
    con filtros estructurados via metadata (edad, tipo_fractura, imc, ...)."""
    settings = get_settings()
    embedder = get_text_embedder()
    ensure_collection(len(embedder.embed_query("")))
    return QdrantVectorStore(
        client=get_qdrant_client(),
        collection_name=settings.qdrant_collection,
        embedding=embedder,
    )

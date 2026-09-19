from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "orthopedic_cases"

    # Mongo guarda los RESULTADOS de salida (informes generados), no el dataset de entrada.
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "recovery_ia"
    mongodb_reports_collection: str = "reports"

    anthropic_api_key: str = ""
    llm_model: str = "claude-sonnet-5"

    text_embedding_model: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

    api_host: str = "0.0.0.0"
    api_port: int = 8000


@lru_cache
def get_settings() -> Settings:
    return Settings()

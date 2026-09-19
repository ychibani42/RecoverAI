from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "orthopedic_cases"

    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "recovery_ia"
    # Informes generados (RESULTADOS de salida) para cada consulta de paciente.
    mongodb_reports_collection: str = "reports"
    # Dataset historico de pacientes sinteticos (ver scripts/ingest_mongo_patients.py),
    # usado por /patients para la tabla de referencia en el frontend.
    mongodb_patients_collection: str = "patients"

    nebius_api_key: str = ""
    llm_model: str = "Qwen/Qwen3-32B"

    text_embedding_model: str = "Qwen/Qwen3-Embedding-8B"

    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # SMS de citas (Vonage Messages API)
    vonage_api_key: str = ""
    vonage_api_secret: str = ""
    vonage_sms_from: str = "RecoverIA"


@lru_cache
def get_settings() -> Settings:
    return Settings()

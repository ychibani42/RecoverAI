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

    # Origenes permitidos para CORS (frontend), separados por comas. Anadir
    # aqui la URL publica del frontend en produccion (ver ai/.env.example).
    cors_allowed_origins: str = "http://localhost:8080,http://127.0.0.1:8080"

    @property
    def cors_allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]

    # SMS de citas (Vonage Messages API)
    vonage_api_key: str = ""
    vonage_api_secret: str = ""
    vonage_sms_from: str = "RecoverIA"

    # Dictado por voz del informe medico (Speech-to-Text de SLNG, modelo
    # Deepgram Nova 3)
    slng_api_key: str = ""
    slng_region: str = "eu-west"

    # Autenticacion del profesional que usa la herramienta (login unico, sin
    # gestion de usuarios). Cambiar en produccion via variables de entorno.
    admin_username: str = "admin"
    admin_password: str = "admin"
    auth_secret_key: str = "change-me-in-production"
    auth_token_ttl_hours: int = 12


@lru_cache
def get_settings() -> Settings:
    return Settings()

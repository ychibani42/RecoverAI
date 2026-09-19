from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from recovery_ia.api.routes import query

app = FastAPI(
    title="recovery-ia",
    description="RAG de casos similares para planificacion de recuperacion ortopedica",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from recovery_ia.api.routes import patients, query, sms
from recovery_ia.sms import start_reminder_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = start_reminder_scheduler()
    yield
    scheduler.shutdown()


app = FastAPI(
    title="recovery-ia",
    description="RAG de casos similares para planificacion de recuperacion ortopedica",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query.router)
app.include_router(patients.router)
app.include_router(sms.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from recovery_ia.api.routes import auth, patients, query, sms, transcription
from recovery_ia.api.security import require_auth
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

app.include_router(auth.router)
app.include_router(query.router, dependencies=[Depends(require_auth)])
app.include_router(patients.router, dependencies=[Depends(require_auth)])
app.include_router(sms.router, dependencies=[Depends(require_auth)])
app.include_router(transcription.router, dependencies=[Depends(require_auth)])

# Sirve las radiografias indexadas (data/images/xrays, xrays_reales) para que
# el frontend pueda mostrarlas junto a los casos similares recuperados.
app.mount("/images", StaticFiles(directory="data/images"), name="images")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

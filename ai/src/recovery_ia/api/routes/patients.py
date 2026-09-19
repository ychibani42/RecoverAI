from fastapi import APIRouter

from recovery_ia.storage import get_patients_collection

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("")
def list_patients() -> list[dict]:
    """Dataset historico de pacientes sinteticos (coleccion MongoDB `patients`,
    cargada por scripts/ingest_mongo_patients.py), para visualizacion en el frontend."""
    return [{k: v for k, v in doc.items() if k != "_id"} for doc in get_patients_collection().find()]

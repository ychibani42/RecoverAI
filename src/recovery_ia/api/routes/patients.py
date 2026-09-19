import json
from pathlib import Path

from fastapi import APIRouter

router = APIRouter(prefix="/patients", tags=["patients"])

DATASET_PATH = Path("data/patients.json")


@router.get("")
def list_patients() -> list[dict]:
    """Dataset historico de pacientes sinteticos (data/patients.json), para visualizacion en el frontend."""
    if not DATASET_PATH.exists():
        return []
    return json.loads(DATASET_PATH.read_text(encoding="utf-8"))

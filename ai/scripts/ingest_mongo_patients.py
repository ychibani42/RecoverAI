"""Carga data/raw/patients.json en MongoDB, coleccion `patients`.

Es la coleccion que sirve /patients (tabla de referencia del dataset historico
en el frontend). Separado de ingest_vector_db.py porque ese ingesta el mismo
fichero fuente en Qdrant para busqueda semantica: mismo origen, dos destinos
con usos distintos.

Uso:
  py scripts/ingest_mongo_patients.py
"""

import json
import sys
from pathlib import Path

from pymongo import UpdateOne

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from recovery_ia.storage import get_patients_collection  # noqa: E402


def main():
    patients_path = ROOT / "data" / "raw" / "patients.json"
    cases = json.loads(patients_path.read_text(encoding="utf-8"))

    collection = get_patients_collection()
    operations = [
        UpdateOne({"case_id": case["case_id"]}, {"$set": case}, upsert=True) for case in cases
    ]
    result = collection.bulk_write(operations)

    print(
        f"Sincronizados {len(cases)} pacientes en MongoDB "
        f"({result.upserted_count} nuevos, {result.modified_count} actualizados)."
    )


if __name__ == "__main__":
    main()

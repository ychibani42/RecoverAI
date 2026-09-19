"""Ingesta data/raw/patients.json en Qdrant usando LangChain.

Cada caso se indexa como un Document cuyo contenido embebido es la nota
diagnostica (texto libre) y cuyo metadata es el resto de campos estructurados
(edad, tipo de fractura, IMC...), usados despues como filtro en Qdrant.

Uso:
  py scripts/ingest_vector_db.py
"""

import json
import sys
import uuid
from pathlib import Path

from langchain_core.documents import Document

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from recovery_ia.vectorstore import get_vectorstore  # noqa: E402


def main():
    patients_path = ROOT / "data" / "raw" / "patients.json"
    cases = json.loads(patients_path.read_text(encoding="utf-8"))

    documents = []
    for case in cases:
        metadata = dict(case)
        metadata["comorbidities"] = case["comorbidities"].split(";") if case["comorbidities"] else []
        documents.append(
            Document(
                page_content=case["diagnosis_note"],
                metadata=metadata,
            )
        )

    vectorstore = get_vectorstore()
    # Qdrant solo acepta como point ID un entero sin signo o un UUID; patient_id
    # (p.ej. "SYN-00001") no vale, asi que se deriva un UUID deterministico a
    # partir de el (queda estable entre re-ingestas) y se conserva el original
    # en el metadata para filtrar/mostrar.
    ids = [str(uuid.uuid5(uuid.NAMESPACE_DNS, c["patient_id"])) for c in cases]
    vectorstore.add_documents(documents, ids=ids)

    print(f"Indexados {len(documents)} casos en Qdrant.")


if __name__ == "__main__":
    main()

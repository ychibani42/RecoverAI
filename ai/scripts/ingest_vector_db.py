"""Ingesta data/raw/patients.json en Qdrant usando LangChain.

Cada caso se indexa como un Document cuyo contenido embebido es la nota
diagnostica (texto libre) y cuyo metadata es el resto de campos estructurados
(edad, tipo de fractura, IMC...), usados despues como filtro en Qdrant. El
metadata incluye ademas image_path, la ruta absoluta resuelta a partir de
imagen_radiografia hacia data/images/xrays/ (radiografias sinteticas) o
data/images/xrays_reales/ (radiografias reales).

Uso:
  py scripts/ingest_vector_db.py
"""

import json
import sys
import uuid
from pathlib import Path

from langchain_core.documents import Document

ROOT = Path(__file__).resolve().parents[1]
IMAGES_DIR = ROOT / "data" / "images"
sys.path.insert(0, str(ROOT / "src"))

from recovery_ia.vectorstore import get_vectorstore  # noqa: E402


def _resolve_image_path(case: dict) -> str | None:
    """Resuelve imagen_radiografia (ruta relativa a data/images/, p.ej.
    'xrays/CASE-0001.png' o 'xrays_reales/real_mano_01.jpg') a una ruta
    absoluta, comprobando que el archivo existe."""
    rel_path = case.get("imagen_radiografia")
    if not rel_path:
        return None
    abs_path = IMAGES_DIR / rel_path
    if not abs_path.is_file():
        print(f"Aviso: {case['case_id']} referencia una imagen inexistente: {abs_path}")
        return None
    return str(abs_path)


def main():
    patients_path = ROOT / "data" / "raw" / "patients.json"
    cases = json.loads(patients_path.read_text(encoding="utf-8"))

    documents = []
    for case in cases:
        metadata = dict(case)
        metadata["image_path"] = _resolve_image_path(case)
        documents.append(
            Document(
                page_content=case["diagnostico_texto"],
                metadata=metadata,
            )
        )

    vectorstore = get_vectorstore()
    # Qdrant solo acepta como point ID un entero sin signo o un UUID; case_id
    # (p.ej. "CASE-00001") no vale, asi que se deriva un UUID deterministico a
    # partir de el (queda estable entre re-ingestas) y se conserva el original
    # en el metadata para filtrar/mostrar.
    ids = [str(uuid.uuid5(uuid.NAMESPACE_DNS, c["case_id"])) for c in cases]
    vectorstore.add_documents(documents, ids=ids)

    print(f"Indexados {len(documents)} casos en Qdrant.")


if __name__ == "__main__":
    main()

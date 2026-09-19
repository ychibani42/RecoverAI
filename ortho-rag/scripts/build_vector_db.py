#!/usr/bin/env python3
"""
Construye la base de datos vectorial (ChromaDB) a partir de los casos
sinteticos generados por generate_synthetic_data.py.

Cada caso se indexa como:
  - "documento" (texto embebido): diagnostico + hallazgos de imagen + plan de
    recuperacion -> esto es lo que se compara semanticamente.
  - "metadata" (filtros estructurados): edad, imc, sexo, tipo de fractura,
    zona, gravedad, nivel de actividad, tratamiento, semanas de recuperacion,
    etc. -> esto es lo que se usa para filtrar de forma estricta antes o
    despues de la busqueda semantica (ej. "solo fracturas de humero",
    "edad entre 60 y 80").

Sobre los embeddings:
    Este entorno de hackathon no tiene salida de red hacia HuggingFace, asi
    que en lugar del modelo de embeddings por defecto de Chroma (que se
    descarga la primera vez) se usa un vectorizador TF-IDF local de
    scikit-learn, entrenado sobre el propio corpus de casos. Es 100% offline
    y reproducible. El vectorizador se guarda (pickle) junto a la base de
    datos para que query_similar_cases.py pueda vectorizar consultas nuevas
    de forma consistente.

    Para produccion, sustituir por un modelo de embeddings clinico real
    (ej. un modelo de sentence-transformers, o un embedding multimodal que
    incluya las radiografias) simplemente reemplazando `vectorize()` y
    `fit_vectorizer()` por las llamadas a ese modelo; el resto del pipeline
    (Chroma, metadata, filtros) no cambia.

Uso:
    python3 build_vector_db.py --in ../data/patients.json --db ../db/chroma
"""

import argparse
import json
import pickle
from pathlib import Path

import chromadb
from sklearn.feature_extraction.text import TfidfVectorizer


def build_document_text(p: dict) -> str:
    """Texto que se convierte en embedding. Junta lo clinicamente relevante
    para que la busqueda semantica capture similitud de casos, no solo
    palabras clave sueltas."""
    return (
        f"{p['diagnostico_texto']} "
        f"{p['hallazgos_imagen_texto']} "
        f"Plan de recuperacion aplicado: {p['plan_recuperacion_texto']}"
    )


def build_metadata(p: dict) -> dict:
    """Metadata estructurada para filtros exactos (where clauses) en Chroma.
    Chroma solo admite tipos escalares (str/int/float/bool) en metadata,
    asi que las listas se aplanan a strings."""
    return {
        "case_id": p["case_id"],
        "sexo": p["sexo"],
        "edad": p["edad"],
        "imc": p["imc"],
        "nivel_actividad": p["nivel_actividad"],
        "deportista": p["deportista"],
        "fractura_tipo": p["fractura_tipo"],
        "fractura_zona": p["fractura_zona"],
        "gravedad": p["gravedad"],
        "mecanismo_lesion": p["mecanismo_lesion"],
        "comorbilidades": ", ".join(p["comorbilidades"]),
        "tratamiento": p["tratamiento"],
        "tratamiento_detalle": p["tratamiento_detalle"],
        "semanas_recuperacion_total": p["semanas_recuperacion_total"],
        "semanas_estabilizacion": p["semanas_estabilizacion"],
        "semanas_fisioterapia": p["semanas_fisioterapia"],
        "complicaciones": p["complicaciones"],
        "puntuacion_resultado": p["puntuacion_resultado"],
        "plan_recuperacion_texto": p["plan_recuperacion_texto"],
    }


def main():
    parser = argparse.ArgumentParser(description="Indexa los casos en ChromaDB")
    parser.add_argument("--in", dest="input", type=str, default="../data/patients.json")
    parser.add_argument("--db", type=str, default="../db/chroma")
    parser.add_argument("--collection", type=str, default="ortho_cases")
    args = parser.parse_args()

    input_path = Path(__file__).parent / args.input
    db_path = Path(__file__).parent / args.db
    db_path.parent.mkdir(parents=True, exist_ok=True)

    pacientes = json.loads(input_path.read_text(encoding="utf-8"))
    print(f"Cargados {len(pacientes)} casos desde {input_path.resolve()}")

    documents = [build_document_text(p) for p in pacientes]

    # --- Vectorizacion TF-IDF local (offline) ---
    vectorizer = TfidfVectorizer(
        max_features=512,
        ngram_range=(1, 2),
        strip_accents="unicode",
        lowercase=True,
    )
    vectors = vectorizer.fit_transform(documents).toarray().tolist()

    vectorizer_path = db_path.parent / "tfidf_vectorizer.pkl"
    with open(vectorizer_path, "wb") as f:
        pickle.dump(vectorizer, f)
    print(f"Vectorizador TF-IDF guardado en: {vectorizer_path.resolve()}")

    client = chromadb.PersistentClient(path=str(db_path))

    # Si ya existe la coleccion de una ejecucion previa, la recreamos para
    # que la indexacion sea reproducible (idempotente) en un hackathon.
    try:
        client.delete_collection(args.collection)
    except Exception:
        pass

    collection = client.create_collection(
        name=args.collection,
        metadata={"hnsw:space": "cosine"},
    )

    ids = [p["case_id"] for p in pacientes]
    metadatas = [build_metadata(p) for p in pacientes]

    # Insercion por lotes (evita problemas de memoria/tiempo con datasets grandes)
    batch_size = 64
    for i in range(0, len(pacientes), batch_size):
        j = min(i + batch_size, len(pacientes))
        collection.add(
            ids=ids[i:j],
            documents=documents[i:j],
            metadatas=metadatas[i:j],
            embeddings=vectors[i:j],
        )
        print(f"  indexados {j}/{len(pacientes)}")

    print(f"\nBase de datos vectorial creada en: {db_path.resolve()}")
    print(f"Coleccion: '{args.collection}' con {collection.count()} casos indexados.")


if __name__ == "__main__":
    main()

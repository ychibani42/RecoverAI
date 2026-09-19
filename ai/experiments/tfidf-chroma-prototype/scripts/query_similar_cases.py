#!/usr/bin/env python3
"""
Motor de consulta "pacientes similares a este" (nucleo del RAG).

Flujo:
  1. Se recibe una consulta de un paciente NUEVO: atributos estructurados
     (edad, sexo, IMC, tipo de fractura, nivel de actividad...) + un texto
     libre opcional (notas de diagnostico / imagen).
  2. Se aplican FILTROS ESTRICTOS opcionales sobre la metadata (ej. solo
     mismo tipo de fractura, o rango de edad) -> esto es lo que en el
     documento del hackathon se llama "filtros estructurados".
  3. Sobre el subconjunto filtrado (o toda la coleccion si no hay filtros),
     se hace busqueda por similitud vectorial (vecinos mas cercanos) usando
     el mismo vectorizador TF-IDF con el que se indexo la base de datos.
  4. Se devuelven los 5-10 casos mas parecidos con su protocolo de
     recuperacion, duracion y resultado -> esto es lo que un agente/chatbot
     citaria como fuente en su respuesta.

Uso como script (linea de comandos), ejemplo:

    python3 query_similar_cases.py \
        --edad 72 --sexo Hombre --fractura "Fractura de cuello femoral" \
        --imc 27.5 --nivel-actividad "moderadamente activo" \
        --k 5

Tambien se puede importar y usar la funcion `find_similar_cases()` desde
un agente/chatbot (ver docstring de esa funcion).
"""

import argparse
import json
import pickle
from pathlib import Path

import chromadb

SCRIPT_DIR = Path(__file__).parent
DEFAULT_DB_PATH = SCRIPT_DIR / "../db/chroma"
DEFAULT_VECTORIZER_PATH = SCRIPT_DIR / "../db/tfidf_vectorizer.pkl"
DEFAULT_COLLECTION = "ortho_cases"


def _load_vectorizer(path: Path):
    with open(path, "rb") as f:
        return pickle.load(f)


def _build_query_text(edad, sexo, fractura, imc, nivel_actividad, notas_libres):
    """Construye el texto de consulta en el mismo 'formato' que los
    documentos indexados, para que el TF-IDF compare cosas comparables."""
    partes = []
    if fractura:
        partes.append(f"{fractura}")
    if sexo:
        partes.append(f"paciente {sexo.lower()}")
    if edad is not None:
        partes.append(f"de {edad} anhos")
    if imc is not None:
        partes.append(f"IMC {imc}")
    if nivel_actividad:
        partes.append(f"nivel de actividad {nivel_actividad}")
    if notas_libres:
        partes.append(notas_libres)
    return ", ".join(partes)


def find_similar_cases(
    edad: int | None = None,
    sexo: str | None = None,
    fractura: str | None = None,
    imc: float | None = None,
    nivel_actividad: str | None = None,
    notas_libres: str | None = None,
    edad_rango: int = 15,
    filtrar_por_fractura: bool = True,
    k: int = 5,
    db_path: Path = DEFAULT_DB_PATH,
    vectorizer_path: Path = DEFAULT_VECTORIZER_PATH,
    collection_name: str = DEFAULT_COLLECTION,
):
    """
    Devuelve los k casos historicos mas similares a un paciente nuevo.

    Esta es la funcion que un agente/chatbot debe llamar como "tool" tras
    extraer los atributos estructurados de la consulta en lenguaje natural
    del profesional sanitario (ej. "hombre, 70 anhos, fractura de humero,
    IMC 28, deportista no").

    Parametros:
        edad, sexo, fractura, imc, nivel_actividad: atributos estructurados
            del paciente nuevo (todos opcionales, pero cuantos mas se den,
            mejor la similitud).
        notas_libres: texto clinico libre adicional (opcional).
        edad_rango: al filtrar, se admite +/- este numero de anhos.
        filtrar_por_fractura: si True, restringe la busqueda a casos con el
            mismo tipo de fractura antes de rankear por similitud semantica
            (recomendado: evita comparar fracturas distintas).
        k: numero de casos similares a devolver (5-10 recomendado).

    Devuelve:
        list[dict] con los campos: case_id, distancia (menor = mas similar),
        y toda la metadata clinica del caso (incluye plan de recuperacion,
        semanas de recuperacion, complicaciones, resultado).
    """
    vectorizer = _load_vectorizer(vectorizer_path)
    client = chromadb.PersistentClient(path=str(db_path))
    collection = client.get_collection(collection_name)

    # --- 1. Filtros estructurados (metadata) ---
    where_clauses = []
    if filtrar_por_fractura and fractura:
        where_clauses.append({"fractura_tipo": fractura})
    if edad is not None:
        where_clauses.append({"edad": {"$gte": max(0, edad - edad_rango)}})
        where_clauses.append({"edad": {"$lte": edad + edad_rango}})

    where = None
    if len(where_clauses) == 1:
        where = where_clauses[0]
    elif len(where_clauses) > 1:
        where = {"$and": where_clauses}

    # --- 2. Vectorizar la consulta con el MISMO vectorizador del indice ---
    query_text = _build_query_text(edad, sexo, fractura, imc, nivel_actividad, notas_libres)
    query_vector = vectorizer.transform([query_text]).toarray().tolist()

    # --- 3. Busqueda por similitud vectorial (con fallback si el filtro deja 0 resultados) ---
    result = collection.query(
        query_embeddings=query_vector,
        n_results=k,
        where=where,
    )

    if not result["ids"][0] and where is not None:
        # Si el filtro es demasiado estricto (p.ej. tipo de fractura poco
        # comun + rango de edad estrecho), reintenta sin filtro de edad.
        result = collection.query(
            query_embeddings=query_vector,
            n_results=k,
            where=where_clauses[0] if where_clauses else None,
        )

    casos = []
    ids = result["ids"][0]
    distancias = result["distances"][0]
    metadatas = result["metadatas"][0]
    for case_id, dist, meta in zip(ids, distancias, metadatas):
        casos.append({
            "case_id": case_id,
            "similitud": round(1 - dist, 4),  # 1 = identico, 0 = nada parecido (distancia coseno)
            **meta,
        })

    return casos


def _print_casos(casos, query_desc):
    print(f"\nConsulta: {query_desc}")
    print(f"Casos similares encontrados: {len(casos)}\n")
    for i, c in enumerate(casos, 1):
        print(f"#{i} — {c['case_id']}  (similitud: {c['similitud']})")
        print(f"    Perfil: {c['sexo']}, {c['edad']} anhos, IMC {c['imc']}, {c['nivel_actividad']}")
        print(f"    Fractura: {c['fractura_tipo']} ({c['fractura_zona']}, gravedad {c['gravedad']})")
        print(f"    Tratamiento: {c['tratamiento']} — {c['tratamiento_detalle']}")
        print(f"    Recuperacion total: {c['semanas_recuperacion_total']} semanas "
              f"({c['semanas_estabilizacion']} estabilizacion + {c['semanas_fisioterapia']} fisioterapia)")
        print(f"    Complicaciones: {c['complicaciones']}  |  Resultado: {c['puntuacion_resultado']}/100")
        print()


def main():
    parser = argparse.ArgumentParser(description="Busca pacientes/casos similares en la base vectorial")
    parser.add_argument("--edad", type=int, default=None)
    parser.add_argument("--sexo", type=str, default=None, choices=["Hombre", "Mujer"])
    parser.add_argument("--fractura", type=str, default=None, help="ej. 'Fractura de cuello femoral'")
    parser.add_argument("--imc", type=float, default=None)
    parser.add_argument("--nivel-actividad", type=str, default=None,
                         choices=["sedentario", "moderadamente activo", "activo", "deportista federado"])
    parser.add_argument("--notas", type=str, default=None, help="texto clinico libre adicional")
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--no-filtrar-fractura", action="store_true",
                         help="no restringir la busqueda al mismo tipo de fractura")
    parser.add_argument("--json", action="store_true", help="imprimir resultado como JSON")
    args = parser.parse_args()

    casos = find_similar_cases(
        edad=args.edad,
        sexo=args.sexo,
        fractura=args.fractura,
        imc=args.imc,
        nivel_actividad=args.nivel_actividad,
        notas_libres=args.notas,
        filtrar_por_fractura=not args.no_filtrar_fractura,
        k=args.k,
    )

    if args.json:
        print(json.dumps(casos, ensure_ascii=False, indent=2))
    else:
        desc = f"{args.sexo or '?'}, {args.edad or '?'} anhos, {args.fractura or 'sin especificar fractura'}, IMC {args.imc or '?'}, {args.nivel_actividad or '?'}"
        _print_casos(casos, desc)


if __name__ == "__main__":
    main()

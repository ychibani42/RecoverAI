from qdrant_client.models import FieldCondition, Filter, MatchValue, Range

from recovery_ia.schemas import PatientCase, SimilarCaseQuery, SimilarCaseResult
from recovery_ia.vectorstore import get_vectorstore

from .weights import FIELD_WEIGHTS, field_distance

# Relacion de mezcla entre la similitud semantica (Qdrant) y la distancia
# estructurada ponderada al calcular el orden final de los casos.
SEMANTIC_WEIGHT = 0.6
STRUCTURED_WEIGHT = 0.4

# Candidatos extra recuperados de Qdrant antes del re-ranking ponderado, para
# no perder casos que el re-ranking pueda subir por encima del top_k original.
CANDIDATE_POOL_MULTIPLIER = 3


def _build_structured_filter(query: SimilarCaseQuery) -> Filter | None:
    """Traduce los factores estructurados de la consulta (sexo, rango de
    edad...) en un filtro nativo de Qdrant, aplicado junto a la busqueda
    semantica sobre la nota diagnostica.

    fractura_tipo no se usa como filtro exacto: el dataset lo almacena como
    descripcion clinica larga (p.ej. "Fractura de radio distal (Colles)"),
    mientras que la extraccion produce una etiqueta corta (p.ej.
    "muneca_colles") para uso interno; un match exacto entre ambos nunca
    coincide y dejaria el filtro sin resultados. La similitud de tipo de
    fractura ya la aporta la busqueda semantica sobre diagnostico_texto.

    Los campos estructurados se guardan en Qdrant anidados bajo la clave
    "metadata" (metadata_payload_key por defecto de QdrantVectorStore), no en
    la raiz del payload, asi que las condiciones deben apuntar a
    "metadata.<campo>"."""
    conditions = []

    if query.sexo:
        conditions.append(FieldCondition(key="metadata.sexo", match=MatchValue(value=query.sexo)))
    if query.edad is not None:
        conditions.append(
            FieldCondition(key="metadata.edad", range=Range(gte=query.edad - 10, lte=query.edad + 10))
        )
    if query.imc is not None:
        conditions.append(FieldCondition(key="metadata.imc", range=Range(gte=query.imc - 5, lte=query.imc + 5)))

    return Filter(must=conditions) if conditions else None


def _weighted_structured_distance(query: SimilarCaseQuery, case: PatientCase) -> float | None:
    """Distancia ponderada [0, 1] entre el paciente nuevo y un caso, usando
    solo los campos ponderados que se conocen del paciente nuevo. None si no
    se conoce ningun campo ponderado (no se puede calcular)."""
    query_values = {
        "edad": query.edad,
        "gravedad": query.gravedad,
        "comorbilidades": query.comorbilidades,
        "imc": query.imc,
        "nivel_actividad": query.nivel_actividad,
        "deportista": query.deportista,
    }

    total_weight = 0.0
    weighted_sum = 0.0
    for field, weight in FIELD_WEIGHTS.items():
        valor_paciente = query_values[field]
        if valor_paciente is None:
            continue
        weighted_sum += weight * field_distance(field, valor_paciente, getattr(case, field))
        total_weight += weight

    if total_weight == 0.0:
        return None
    return weighted_sum / total_weight


def find_similar_cases(query: SimilarCaseQuery) -> list[SimilarCaseResult]:
    """Recupera los casos historicos mas parecidos: similitud semantica sobre
    la nota diagnostica + filtros estructurados sobre el payload de Qdrant,
    re-rankeados por una distancia ponderada sobre los factores clinicos que
    mas deben pesar (edad, gravedad, comorbilidades...)."""
    vectorstore = get_vectorstore()
    qdrant_filter = _build_structured_filter(query)

    docs_with_scores = vectorstore.similarity_search_with_score(
        query.free_text,
        k=query.top_k * CANDIDATE_POOL_MULTIPLIER,
        filter=qdrant_filter,
    )

    results = []
    for doc, score in docs_with_scores:
        case = PatientCase(**doc.metadata)
        structured_distance = _weighted_structured_distance(query, case)
        final_score = (
            SEMANTIC_WEIGHT * score + STRUCTURED_WEIGHT * (1 - structured_distance)
            if structured_distance is not None
            else score
        )
        results.append(
            SimilarCaseResult(
                case=case,
                similarity_score=score,
                structured_distance=structured_distance,
                final_score=final_score,
            )
        )

    results.sort(key=lambda r: r.final_score, reverse=True)
    return results[: query.top_k]

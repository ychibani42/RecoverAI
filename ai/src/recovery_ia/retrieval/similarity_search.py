from qdrant_client.models import FieldCondition, Filter, MatchValue, Range

from recovery_ia.schemas import PatientCase, SimilarCaseQuery, SimilarCaseResult
from recovery_ia.vectorstore import get_vectorstore


def _build_structured_filter(query: SimilarCaseQuery) -> Filter | None:
    """Traduce los factores estructurados de la consulta (tipo de fractura,
    rango de edad...) en un filtro nativo de Qdrant, aplicado junto a la
    busqueda semantica sobre la nota diagnostica."""
    conditions = []

    if query.fractura_tipo:
        conditions.append(FieldCondition(key="fractura_tipo", match=MatchValue(value=query.fractura_tipo)))
    if query.sexo:
        conditions.append(FieldCondition(key="sexo", match=MatchValue(value=query.sexo)))
    if query.edad is not None:
        conditions.append(FieldCondition(key="edad", range=Range(gte=query.edad - 10, lte=query.edad + 10)))
    if query.imc is not None:
        conditions.append(FieldCondition(key="imc", range=Range(gte=query.imc - 5, lte=query.imc + 5)))

    return Filter(must=conditions) if conditions else None


def find_similar_cases(query: SimilarCaseQuery) -> list[SimilarCaseResult]:
    """Recupera los casos historicos mas parecidos: similitud semantica sobre
    la nota diagnostica + filtros estructurados sobre el payload de Qdrant."""
    vectorstore = get_vectorstore()
    qdrant_filter = _build_structured_filter(query)

    docs_with_scores = vectorstore.similarity_search_with_score(
        query.free_text,
        k=query.top_k,
        filter=qdrant_filter,
    )

    results = []
    for doc, score in docs_with_scores:
        case = PatientCase(**doc.metadata)
        results.append(SimilarCaseResult(case=case, similarity_score=score))
    return results

from qdrant_client.models import FieldCondition, Filter, MatchValue, Range

from recovery_ia.schemas import PatientCase, SimilarCaseQuery, SimilarCaseResult
from recovery_ia.vectorstore import get_vectorstore


def _build_structured_filter(query: SimilarCaseQuery) -> Filter | None:
    """Traduce los factores estructurados de la consulta (tipo de fractura,
    rango de edad...) en un filtro nativo de Qdrant, aplicado junto a la
    busqueda semantica sobre la nota diagnostica."""
    conditions = []

    if query.fracture_type:
        conditions.append(FieldCondition(key="fracture_type", match=MatchValue(value=query.fracture_type)))
    if query.sex:
        conditions.append(FieldCondition(key="sex", match=MatchValue(value=query.sex)))
    if query.age is not None:
        conditions.append(FieldCondition(key="age", range=Range(gte=query.age - 10, lte=query.age + 10)))
    if query.bmi is not None:
        conditions.append(FieldCondition(key="bmi", range=Range(gte=query.bmi - 5, lte=query.bmi + 5)))
    if query.lab_vitamina_d_ng_ml is not None:
        conditions.append(
            FieldCondition(
                key="lab_vitamina_d_ng_ml",
                range=Range(gte=query.lab_vitamina_d_ng_ml - 10, lte=query.lab_vitamina_d_ng_ml + 10),
            )
        )
    if query.lab_glucosa_mg_dl is not None:
        conditions.append(
            FieldCondition(
                key="lab_glucosa_mg_dl",
                range=Range(gte=query.lab_glucosa_mg_dl - 30, lte=query.lab_glucosa_mg_dl + 30),
            )
        )

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

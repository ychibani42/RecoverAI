from langchain_core.prompts import ChatPromptTemplate

from recovery_ia.retrieval import find_similar_cases
from recovery_ia.schemas import ClinicalReport, NewPatientInput, SimilarCaseQuery, SimilarCaseResult

from .extraction import extract_query_from_report
from .llm import get_llm

REPORT_SYSTEM_PROMPT = """Eres un asistente clinico de apoyo a la decision para \
traumatologia y ortopedia. Recibes el caso de un paciente nuevo y una lista de casos \
historicos similares (cada uno con su nota diagnostica, protocolo, plazo de recuperacion \
y resultado), seleccionados por semejanza clinica y radiografica con el caso consultado. \
A partir UNICAMENTE de esos casos, redacta un informe con:
- Resumen de los casos similares y por que se parecen al caso consultado (incluyendo, \
cuando proceda, la semejanza radiografica).
- Tratamiento recomendado (conservador o quirurgico, con detalle) basado en lo que \
funciono en esos casos.
- Tiempo de recuperacion estimado (rango de semanas), justificado por los casos.
- Semanas hasta la cita de revision recomendada (numero entero), coherente con ese rango.
- Dieta recomendada UNICAMENTE si es relevante (consolidacion osea, comorbilidades como \
diabetes, obesidad u osteoporosis); si no aplica, indicalo como null.
- Habitos de salud recomendados durante la recuperacion (actividad fisica, tabaco/alcohol, \
adherencia a fisioterapia, etc.).
- Una advertencia de que es una orientacion de apoyo a la decision, no un diagnostico, y \
no sustituye el criterio clinico del profesional.

Redacta todo el informe (todos los campos) en el idioma indicado por el codigo \
ISO 639-1 que se te proporcione, independientemente del idioma del informe o los \
casos historicos de entrada.
"""

LANGUAGE_NAMES = {
    "es": "español",
    "en": "English",
    "fr": "français",
    "ca": "català",
    "de": "Deutsch",
}


def _build_context(similar_cases: list[SimilarCaseResult]) -> str:
    return "\n\n".join(
        f"Caso {r.case.case_id} (similitud {r.similarity_score:.2f}): "
        f"{r.case.diagnostico_texto} Tratamiento: {r.case.tratamiento_detalle}, "
        f"recuperacion {r.case.semanas_recuperacion_total} semanas "
        f"(estabilizacion {r.case.semanas_estabilizacion}, fisioterapia {r.case.semanas_fisioterapia}), "
        f"complicaciones: {r.case.complicaciones}. Plan: {r.case.plan_recuperacion_texto}"
        for r in similar_cases
    )


def generate_report_from_query(query: SimilarCaseQuery) -> tuple[ClinicalReport, list[SimilarCaseResult]]:
    """Pipeline RAG: recupera casos similares en Qdrant y pide al LLM que
    redacte el informe clinico estructurado a partir de ese contexto.

    Devuelve tambien los casos similares usados, para poder archivarlos junto
    al informe (ver recovery_ia.storage)."""
    similar_cases = find_similar_cases(query)
    context = _build_context(similar_cases)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", REPORT_SYSTEM_PROMPT),
            (
                "human",
                "Idioma de salida (ISO 639-1): {language} ({language_name})\n\n"
                "Caso del paciente nuevo: {query}\n\nCasos similares recuperados:\n{context}",
            ),
        ]
    )

    language_name = LANGUAGE_NAMES.get(query.language, query.language)
    structured_llm = get_llm().with_structured_output(ClinicalReport)
    report = structured_llm.invoke(
        prompt.format_messages(
            query=query.free_text,
            context=context,
            language=query.language,
            language_name=language_name,
        )
    )
    return report, similar_cases


def generate_report_from_patient_input(
    patient_input: NewPatientInput,
) -> tuple[ClinicalReport, list[SimilarCaseResult]]:
    """Punto de entrada de alto nivel: informe medico en texto libre (+ radiografia
    opcional) -> extraccion de factores -> busqueda de casos similares -> informe."""
    query = extract_query_from_report(patient_input)
    return generate_report_from_query(query)

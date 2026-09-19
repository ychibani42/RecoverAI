from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from recovery_ia.schemas import NewPatientInput, SimilarCaseQuery

from .llm import get_llm

EXTRACTION_SYSTEM_PROMPT = """Extrae del informe medico y/o analitica de un paciente nuevo los \
factores estructurados necesarios para buscar casos similares: edad, sexo (M/F), tipo de \
fractura (usa una etiqueta corta y consistente, p.ej. "humero_diafisis", "muneca_colles", \
"femur_diafisis", "cadera_cuello_femoral", "tibia_perone", "tobillo_maleolar", "clavicula", \
"vertebral_compresion", "costilla"), IMC si se indica o se puede calcular, y nivel de actividad \
fisica ("sedentario", "moderado" o "deportista"). Si un dato no aparece en el texto, dejalo \
vacio/null. No inventes valores que no esten en el texto."""


class _ExtractedFactors(BaseModel):
    edad: int | None = None
    sexo: str | None = None
    fractura_tipo: str | None = None
    imc: float | None = None
    nivel_actividad: str | None = None


def _combined_diagnostic_text(patient_input: NewPatientInput) -> str:
    """Junta todas las fuentes de texto disponibles del paciente nuevo (informe
    medico + analitica) en un unico texto: es lo que se embebe para la busqueda
    semantica y lo que se pasa al LLM para extraer los factores estructurados."""
    parts = [patient_input.medical_report_text]
    if patient_input.lab_results_text:
        parts.append(f"Analítica: {patient_input.lab_results_text}")
    return "\n".join(parts)


def extract_query_from_report(patient_input: NewPatientInput) -> SimilarCaseQuery:
    """Convierte el informe medico (+ analitica, si se aporta) de un paciente
    nuevo en una consulta estructurada: el texto combinado se usa para la
    busqueda semantica y los factores extraidos como filtros sobre el payload
    de Qdrant."""
    diagnostic_text = _combined_diagnostic_text(patient_input)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", EXTRACTION_SYSTEM_PROMPT),
            ("human", "{diagnostic_text}"),
        ]
    )
    structured_llm = get_llm().with_structured_output(_ExtractedFactors)
    factors = structured_llm.invoke(prompt.format_messages(diagnostic_text=diagnostic_text))

    return SimilarCaseQuery(
        free_text=diagnostic_text,
        xray_image_path=patient_input.xray_image_path,
        top_k=patient_input.top_k,
        language=patient_input.language,
        **factors.model_dump(),
    )

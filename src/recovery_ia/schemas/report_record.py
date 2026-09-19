from datetime import datetime, timezone

from pydantic import BaseModel, Field

from .patient_case import PatientCase
from .query import NewPatientInput
from .report import ClinicalReport


class SimilarCaseRef(BaseModel):
    """Referencia ligera a un caso similar recuperado, tal como se archiva junto al informe."""

    patient_id: str
    similarity_score: float


class ReportRecord(BaseModel):
    """Resultado de salida persistido en MongoDB: la entrada del paciente, los
    casos similares usados como contexto y el informe generado."""

    id: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    patient_input: NewPatientInput
    similar_cases: list[SimilarCaseRef] = []
    report: ClinicalReport


def case_ref_from(case: PatientCase, score: float) -> SimilarCaseRef:
    return SimilarCaseRef(patient_id=case.patient_id, similarity_score=score)

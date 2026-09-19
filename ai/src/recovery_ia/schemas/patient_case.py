from pydantic import BaseModel


class PatientCase(BaseModel):
    """Representa un caso clinico indexado en Qdrant (payload estructurado)."""

    patient_id: str
    age: int
    sex: str
    bmi: float
    activity_level: str
    comorbidities: list[str] = []
    fracture_type: str
    fracture_label: str
    severity: str
    treatment_type: str
    protocol_id: str
    recovery_weeks: int
    outcome: str
    diagnosis_note: str
    followup_note: str
    image_id: str | None = None
    lab_calcio_mg_dl: float | None = None
    lab_vitamina_d_ng_ml: float | None = None
    lab_hemoglobina_g_dl: float | None = None
    lab_glucosa_mg_dl: float | None = None
    lab_pcr_mg_l: float | None = None
    lab_summary: str | None = None

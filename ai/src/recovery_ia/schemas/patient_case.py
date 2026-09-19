from pydantic import BaseModel


class RecoveryMilestone(BaseModel):
    semana: int
    hito: str


class PatientCase(BaseModel):
    """Representa un caso clinico indexado en Qdrant (payload estructurado)."""

    case_id: str
    uuid: str
    sexo: str
    edad: int
    altura_cm: int
    peso_kg: float
    imc: float
    nivel_actividad: str
    deportista: bool
    comorbilidades: list[str] = []
    fractura_tipo: str
    fractura_zona: str
    gravedad: str
    mecanismo_lesion: str
    tratamiento: str
    tratamiento_detalle: str
    diagnostico_texto: str
    hallazgos_imagen_texto: str
    plan_recuperacion_texto: str
    semanas_recuperacion_total: int
    semanas_estabilizacion: int
    semanas_fisioterapia: int
    hitos_recuperacion: list[RecoveryMilestone] = []
    complicaciones: str
    puntuacion_resultado: float
    imagen_radiografia: str | None = None
    imagen_radiografia_sintetica_original: str | None = None
    imagen_radiografia_tipo: str | None = None
    imagen_radiografia_fuente: str | None = None
    # Resuelto por scripts/ingest_vector_db.py a partir de imagen_radiografia; no viene en patients.json.
    image_path: str | None = None

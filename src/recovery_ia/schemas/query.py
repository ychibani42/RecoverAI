from pydantic import BaseModel

from .patient_case import PatientCase


class NewPatientInput(BaseModel):
    """Entrada cruda para un paciente nuevo: lo que llega a la API antes de
    procesar nada. El sistema admite varios tipos de dato diagnostico, no solo
    radiografias:
    - medical_report_text: informe medico en texto libre (ya extraido de un PDF/dictado).
    - lab_results_text: analisis clinicos/analitica en texto libre (ej. "Calcio 8.9 mg/dl,
      Vitamina D 18 ng/ml, Glucosa 145 mg/dl, PCR 12 mg/l").
    - xray_image_path / additional_file_paths: rutas a archivos ya subidos (radiografia y
      otros documentos diagnosticos: informes de laboratorio en PDF, otras pruebas de
      imagen...). Su contenido no estructurado se referencia aqui; el texto que aportan
      para la busqueda debe venir en medical_report_text/lab_results_text.
    """

    medical_report_text: str
    lab_results_text: str | None = None
    xray_image_path: str | None = None
    additional_file_paths: list[str] = []
    top_k: int = 5


class SimilarCaseQuery(BaseModel):
    """Consulta estructurada usada para buscar en Qdrant: combina el texto
    del informe (busqueda semantica) con los factores extraidos de el
    (filtros estructurados sobre el payload). Se obtiene automaticamente a
    partir de un NewPatientInput via recovery_ia.agent.extraction.

    Ej: "hombre, 70 años, fractura de humero, IMC 27, deportista: no"
    """

    free_text: str
    xray_image_path: str | None = None
    age: int | None = None
    sex: str | None = None
    fracture_type: str | None = None
    bmi: float | None = None
    activity_level: str | None = None
    lab_vitamina_d_ng_ml: float | None = None
    lab_glucosa_mg_dl: float | None = None
    top_k: int = 5


class SimilarCaseResult(BaseModel):
    case: PatientCase
    similarity_score: float

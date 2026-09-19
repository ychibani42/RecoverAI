import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from recovery_ia.schemas import ClinicalReport, NewPatientInput, PatientCase, SimilarCaseQuery


def test_patient_case_from_dataset_record():
    record = {
        "case_id": "CASE-0001",
        "uuid": "f21e137a-e954-435f-9664-01db01ec4a1b",
        "sexo": "Hombre",
        "edad": 70,
        "altura_cm": 175,
        "peso_kg": 83.7,
        "imc": 27.3,
        "nivel_actividad": "sedentario",
        "deportista": False,
        "comorbilidades": ["diabetes"],
        "fractura_tipo": "Fractura de diafisis humeral",
        "fractura_zona": "Humero/Diafisis",
        "gravedad": "leve",
        "mecanismo_lesion": "caida accidental",
        "tratamiento": "conservador",
        "tratamiento_detalle": "inmovilizacion con cabestrillo y control radiografico periodico",
        "diagnostico_texto": "...",
        "hallazgos_imagen_texto": "...",
        "plan_recuperacion_texto": "...",
        "semanas_recuperacion_total": 10,
        "semanas_estabilizacion": 4,
        "semanas_fisioterapia": 6,
        "hitos_recuperacion": [{"semana": 4, "hito": "inicio de carga progresiva"}],
        "complicaciones": "ninguna",
        "puntuacion_resultado": 90.0,
        "imagen_radiografia": "xrays/CASE-0001.png",
        "imagen_radiografia_tipo": "sintetica",
        "imagen_radiografia_fuente": "Radiografia sintetica generada proceduralmente.",
    }
    case = PatientCase(**record)
    assert case.case_id == "CASE-0001"


def test_similar_case_query_defaults():
    query = SimilarCaseQuery(free_text="hombre, 70 anios, fractura de humero")
    assert query.top_k == 5


def test_new_patient_input_requires_only_report_text():
    patient_input = NewPatientInput(medical_report_text="Varon de 70 anios, fractura de humero.")
    assert patient_input.xray_image_path is None
    assert patient_input.top_k == 5


def test_clinical_report_diet_and_habits_are_optional():
    report = ClinicalReport(
        resumen_casos_similares="...",
        tratamiento_recomendado="...",
        tiempo_recuperacion_estimado="8-10 semanas",
        semanas_hasta_revision=8,
        advertencia="Orientacion de apoyo, no sustituye el criterio clinico.",
    )
    assert report.dieta_recomendada is None
    assert report.habitos_salud_recomendados is None

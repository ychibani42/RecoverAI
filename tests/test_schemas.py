import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from recovery_ia.schemas import ClinicalReport, NewPatientInput, PatientCase, SimilarCaseQuery


def test_patient_case_from_dataset_record():
    record = {
        "patient_id": "SYN-00001",
        "age": 70,
        "sex": "M",
        "bmi": 27.3,
        "activity_level": "sedentario",
        "comorbidities": ["diabetes"],
        "fracture_type": "humero_diafisis",
        "fracture_label": "Fractura de diafisis humeral",
        "severity": "I - simple",
        "treatment_type": "conservador",
        "protocol_id": "PROT-humero_diafisis-I-con",
        "recovery_weeks": 10,
        "outcome": "recuperacion_completa",
        "diagnosis_note": "...",
        "followup_note": "...",
        "image_id": "SYN-00001.png",
    }
    case = PatientCase(**record)
    assert case.patient_id == "SYN-00001"


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
        advertencia="Orientacion de apoyo, no sustituye el criterio clinico.",
    )
    assert report.dieta_recomendada is None
    assert report.habitos_salud_recomendados is None

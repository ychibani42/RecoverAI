import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from recovery_ia.retrieval.similarity_search import _weighted_structured_distance
from recovery_ia.retrieval.weights import field_distance
from recovery_ia.schemas import PatientCase, SimilarCaseQuery


def _make_case(**overrides) -> PatientCase:
    base = dict(
        case_id="CASE-0001",
        uuid="f21e137a-e954-435f-9664-01db01ec4a1b",
        sexo="Hombre",
        edad=72,
        altura_cm=175,
        peso_kg=83.7,
        imc=27.3,
        nivel_actividad="sedentario",
        deportista=False,
        comorbilidades=["diabetes"],
        fractura_tipo="Fractura de diafisis humeral",
        fractura_zona="Humero/Diafisis",
        gravedad="grave",
        mecanismo_lesion="caida accidental",
        tratamiento="conservador",
        tratamiento_detalle="...",
        diagnostico_texto="...",
        hallazgos_imagen_texto="...",
        plan_recuperacion_texto="...",
        semanas_recuperacion_total=10,
        semanas_estabilizacion=4,
        semanas_fisioterapia=6,
        complicaciones="ninguna",
        puntuacion_resultado=90.0,
    )
    base.update(overrides)
    return PatientCase(**base)


def test_field_distance_edad_normalized():
    assert field_distance("edad", 70, 70) == 0.0
    assert field_distance("edad", 30, 70) == 1.0  # capped at 1.0
    assert field_distance("edad", 60, 70) == 10 / 40


def test_field_distance_gravedad_ordinal():
    assert field_distance("gravedad", "leve", "leve") == 0.0
    assert field_distance("gravedad", "leve", "grave") == 1.0
    assert field_distance("gravedad", "leve", "moderada") == 0.5


def test_field_distance_comorbilidades_overlap():
    assert field_distance("comorbilidades", [], []) == 0.0
    assert field_distance("comorbilidades", ["diabetes"], ["diabetes"]) == 0.0
    assert field_distance("comorbilidades", ["diabetes"], ["obesidad"]) == 1.0


def test_weighted_structured_distance_identical_patient_is_zero():
    case = _make_case()
    query = SimilarCaseQuery(
        free_text="...",
        edad=72,
        gravedad="grave",
        comorbilidades=["diabetes"],
        imc=27.3,
        nivel_actividad="sedentario",
        deportista=False,
    )
    assert _weighted_structured_distance(query, case) == 0.0


def test_weighted_structured_distance_none_when_no_known_fields():
    case = _make_case()
    query = SimilarCaseQuery(free_text="...")
    assert _weighted_structured_distance(query, case) is None


def test_weighted_structured_distance_uses_only_known_fields():
    case = _make_case(edad=72)
    query = SimilarCaseQuery(free_text="...", edad=32)  # 1.0 distance on edad only
    assert _weighted_structured_distance(query, case) == 1.0

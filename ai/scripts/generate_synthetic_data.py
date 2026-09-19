"""
Generador de dataset SINTÉTICO (100% inventado, no proviene de pacientes reales)
para prototipar el pipeline RAG de recovery-ia.

Salidas:
  data/raw/patients.json           -> casos de pacientes (estructurado + nota narrativa)
  data/raw/patients.csv            -> misma info en formato tabular
  data/raw/recovery_protocols.json -> catálogo de protocolos de recuperación por tipo/gravedad
  data/images/{patient_id}.png     -> placeholder sintético de "radiografía" (patrón generado,
                                       NO es una imagen médica real; sirve solo para probar
                                       el pipeline de embeddings de imagen)

Uso:
  py scripts/generate_synthetic_data.py --n 300 --seed 42
"""

import argparse
import csv
import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
IMG_DIR = ROOT / "data" / "images"

FRACTURE_TYPES = {
    "muneca_colles": {
        "label": "Fractura de radio distal (tipo Colles)",
        "base_weeks": 7,
        "surgical_ratio": 0.35,
    },
    "humero_diafisis": {
        "label": "Fractura de diáfisis humeral",
        "base_weeks": 10,
        "surgical_ratio": 0.4,
    },
    "femur_diafisis": {
        "label": "Fractura de diáfisis femoral",
        "base_weeks": 14,
        "surgical_ratio": 0.9,
    },
    "cadera_cuello_femoral": {
        "label": "Fractura de cuello femoral (cadera)",
        "base_weeks": 14,
        "surgical_ratio": 0.85,
    },
    "tibia_perone": {
        "label": "Fractura de tibia y peroné",
        "base_weeks": 13,
        "surgical_ratio": 0.55,
    },
    "tobillo_maleolar": {
        "label": "Fractura maleolar de tobillo",
        "base_weeks": 8,
        "surgical_ratio": 0.3,
    },
    "clavicula": {
        "label": "Fractura de clavícula",
        "base_weeks": 6,
        "surgical_ratio": 0.15,
    },
    "vertebral_compresion": {
        "label": "Fractura vertebral por compresión",
        "base_weeks": 10,
        "surgical_ratio": 0.2,
    },
    "costilla": {
        "label": "Fractura costal",
        "base_weeks": 5,
        "surgical_ratio": 0.02,
    },
}

FRACTURE_WEIGHTS_BY_AGE = {
    # bracket: (max_age_exclusive, weights por fx_key en el mismo orden que FRACTURE_TYPES)
    "child": {
        "muneca_colles": 5, "humero_diafisis": 2, "femur_diafisis": 2,
        "cadera_cuello_femoral": 0.2, "tibia_perone": 3, "tobillo_maleolar": 2,
        "clavicula": 5, "vertebral_compresion": 0.3, "costilla": 1,
    },
    "adult": {
        "muneca_colles": 3, "humero_diafisis": 3, "femur_diafisis": 2.5,
        "cadera_cuello_femoral": 0.5, "tibia_perone": 3, "tobillo_maleolar": 3,
        "clavicula": 2.5, "vertebral_compresion": 1.5, "costilla": 2.5,
    },
    "elderly": {
        "muneca_colles": 4, "humero_diafisis": 3, "femur_diafisis": 2,
        "cadera_cuello_femoral": 5, "tibia_perone": 1.5, "tobillo_maleolar": 1.5,
        "clavicula": 1, "vertebral_compresion": 4, "costilla": 2,
    },
}


def age_bracket(age: int) -> str:
    if age < 18:
        return "child"
    if age < 65:
        return "adult"
    return "elderly"


def pick_fracture_type(rng: random.Random, age: int) -> str:
    weights_map = FRACTURE_WEIGHTS_BY_AGE[age_bracket(age)]
    keys = list(FRACTURE_TYPES.keys())
    weights = [weights_map[k] for k in keys]
    return rng.choices(keys, weights=weights)[0]


SEVERITIES = ["I - simple", "II - desplazada", "III - conminuta"]
SEVERITY_FACTOR = {"I - simple": 1.0, "II - desplazada": 1.15, "III - conminuta": 1.4}

ACTIVITY_LEVELS = ["sedentario", "moderado", "deportista"]
COMORBIDITIES_POOL = ["diabetes", "osteoporosis", "hipertension", "tabaquismo", "obesidad"]

OUTCOME_LABELS = ["recuperacion_completa", "recuperacion_parcial_con_limitacion", "complicacion"]

FIRST_NAMES_F = ["Maria", "Laura", "Ana", "Carmen", "Lucia", "Elena", "Sofia", "Isabel"]
FIRST_NAMES_M = ["Javier", "Antonio", "Carlos", "Manuel", "David", "Pablo", "Jorge", "Miguel"]

FOLLOWUP_PHRASES = [
    "Buena evolución clínica y radiológica en los controles sucesivos.",
    "Evolución favorable, cumple con el programa de fisioterapia pautado.",
    "Ligero retraso en la consolidación, se ajusta el plan de carga progresiva.",
    "Aparece rigidez articular leve, se refuerza la pauta de rehabilitación.",
    "Buena tolerancia al tratamiento, sin incidencias reseñables.",
    "Se detecta dolor residual moderado que limita la actividad deportiva previa.",
]

COMPLICATION_PHRASES = [
    "Retraso de consolidación que requiere prolongar la inmovilización.",
    "Infección superficial de la herida quirúrgica, resuelta con tratamiento antibiótico.",
    "Rigidez articular significativa que limita el rango de movimiento final.",
    "Pseudoartrosis que precisa revisión quirúrgica.",
]


@dataclass
class PatientCase:
    patient_id: str
    age: int
    sex: str
    height_cm: int
    weight_kg: int
    bmi: float
    activity_level: str
    comorbidities: str
    fracture_type: str
    fracture_label: str
    fracture_side: str
    severity: str
    treatment_type: str
    protocol_id: str
    recovery_weeks: int
    outcome: str
    diagnosis_note: str
    followup_note: str
    image_id: str
    lab_calcio_mg_dl: float
    lab_vitamina_d_ng_ml: float
    lab_hemoglobina_g_dl: float
    lab_glucosa_mg_dl: float
    lab_pcr_mg_l: float
    lab_summary: str


def make_bmi(height_cm: int, weight_kg: int) -> float:
    h = height_cm / 100
    return round(weight_kg / (h * h), 1)


MIN_AGE_FOR_COMORBIDITY = {
    "diabetes": 30,
    "osteoporosis": 45,
    "hipertension": 30,
    "tabaquismo": 16,
    "obesidad": 12,
}


def pick_comorbidities(rng: random.Random, age: int) -> list[str]:
    # más comorbilidades a más edad, y solo las clinicamente plausibles para esa edad
    p = 0.15 if age < 50 else (0.35 if age < 70 else 0.55)
    pool = [c for c in COMORBIDITIES_POOL if age >= MIN_AGE_FOR_COMORBIDITY[c]]
    chosen = [c for c in pool if rng.random() < p]
    return chosen


def compute_recovery_weeks(rng: random.Random, base_weeks: float, age: int,
                            comorbidities: list[str], activity_level: str,
                            severity: str, bmi: float) -> int:
    factor = SEVERITY_FACTOR[severity]
    if age >= 65:
        factor *= 1.2
    elif age >= 45:
        factor *= 1.05

    if "osteoporosis" in comorbidities:
        factor *= 1.15
    if "diabetes" in comorbidities:
        factor *= 1.1
    if "tabaquismo" in comorbidities:
        factor *= 1.1
    if "obesidad" in comorbidities or bmi >= 30:
        factor *= 1.08

    if activity_level == "deportista":
        factor *= 0.92

    weeks = base_weeks * factor * rng.uniform(0.9, 1.1)
    return max(3, round(weeks))


def compute_outcome(rng: random.Random, age: int, comorbidities: list[str], severity: str) -> str:
    risk = 0.08
    risk += 0.05 * len(comorbidities)
    if age >= 70:
        risk += 0.08
    if severity == "III - conminuta":
        risk += 0.1

    partial_p = 0.2 + 0.03 * len(comorbidities)
    roll = rng.random()
    if roll < risk:
        return "complicacion"
    if roll < risk + partial_p:
        return "recuperacion_parcial_con_limitacion"
    return "recuperacion_completa"


def generate_lab_results(rng: random.Random, age: int, comorbidities: list[str], severity: str,
                          treatment_type: str) -> dict:
    """Analítica de sangre sintética, con desviaciones ligadas a comorbilidades
    y gravedad (p.ej. hipovitaminosis D en osteoporosis, PCR elevada en
    fracturas graves/postquirúrgicas)."""
    calcio = rng.uniform(8.6, 10.2)
    vitamina_d = rng.uniform(25, 55)
    hemoglobina = rng.uniform(12.5, 16.5)
    glucosa = rng.uniform(75, 100)
    pcr = rng.uniform(0.5, 4.0)

    if "osteoporosis" in comorbidities:
        vitamina_d -= rng.uniform(10, 20)
        calcio -= rng.uniform(0.2, 0.6)
    if "diabetes" in comorbidities:
        glucosa += rng.uniform(40, 90)
    if age >= 70:
        hemoglobina -= rng.uniform(0.5, 1.8)
    if severity == "III - conminuta" or treatment_type == "quirurgico":
        pcr += rng.uniform(3, 15)

    return {
        "lab_calcio_mg_dl": round(max(6.0, calcio), 1),
        "lab_vitamina_d_ng_ml": round(max(5.0, vitamina_d), 1),
        "lab_hemoglobina_g_dl": round(max(8.0, hemoglobina), 1),
        "lab_glucosa_mg_dl": round(glucosa, 1),
        "lab_pcr_mg_l": round(pcr, 1),
    }


def build_lab_summary(labs: dict) -> str:
    flags = []
    if labs["lab_vitamina_d_ng_ml"] < 20:
        flags.append("déficit de vitamina D")
    if labs["lab_calcio_mg_dl"] < 8.5:
        flags.append("hipocalcemia leve")
    if labs["lab_glucosa_mg_dl"] > 126:
        flags.append("glucemia elevada")
    if labs["lab_pcr_mg_l"] > 10:
        flags.append("PCR elevada (marcador inflamatorio)")

    flags_txt = f" Hallazgos relevantes: {', '.join(flags)}." if flags else " Sin hallazgos analíticos relevantes."
    return (
        f"Analítica: calcio {labs['lab_calcio_mg_dl']} mg/dl, vitamina D {labs['lab_vitamina_d_ng_ml']} ng/ml, "
        f"hemoglobina {labs['lab_hemoglobina_g_dl']} g/dl, glucosa {labs['lab_glucosa_mg_dl']} mg/dl, "
        f"PCR {labs['lab_pcr_mg_l']} mg/l.{flags_txt}"
    )


def build_diagnosis_note(rng: random.Random, sex: str, age: int, fracture_label: str,
                          side: str, severity: str, activity_level: str,
                          comorbidities: list[str], bmi: float, lab_summary: str) -> str:
    genero = "varón" if sex == "M" else "mujer"
    comorb_txt = ", ".join(comorbidities) if comorbidities else "sin comorbilidades relevantes"
    return (
        f"Paciente {genero} de {age} años, IMC {bmi}, nivel de actividad física {activity_level}. "
        f"Diagnóstico: {fracture_label}, lado {side}, gravedad {severity}. "
        f"Antecedentes: {comorb_txt}. Estudio radiográfico compatible con el diagnóstico descrito. "
        f"{lab_summary}"
    )


def build_followup_note(rng: random.Random, outcome: str) -> str:
    if outcome == "complicacion":
        return rng.choice(COMPLICATION_PHRASES)
    return rng.choice(FOLLOWUP_PHRASES)


def make_synthetic_xray_image(path: Path, seed: int, fracture_label: str, size: int = 256) -> None:
    """Genera una imagen PLACEHOLDER (patrón sintético, no una radiografía real)
    únicamente para poder probar el pipeline de embeddings de imagen end-to-end."""
    rng = random.Random(seed)
    img = Image.new("L", (size, size), color=10)
    draw = ImageDraw.Draw(img)

    # ruido de fondo tipo "textura ósea" sintética
    for _ in range(400):
        x, y = rng.randint(0, size - 1), rng.randint(0, size - 1)
        v = rng.randint(20, 60)
        draw.point((x, y), fill=v)

    # "hueso" esquemático: una forma alargada con una línea de fractura
    bone_w = rng.randint(30, 50)
    x0 = size // 2 - bone_w // 2
    x1 = size // 2 + bone_w // 2
    draw.rectangle([x0, 20, x1, size - 20], outline=200, fill=140)

    # línea de fractura
    fy = rng.randint(80, size - 80)
    draw.line([(x0 - 5, fy), (x1 + 5, fy + rng.randint(-10, 10))], fill=250, width=3)

    img.save(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=300, help="numero de casos sinteticos a generar")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--skip-images", action="store_true", help="no generar imagenes placeholder")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    IMG_DIR.mkdir(parents=True, exist_ok=True)

    cases: list[PatientCase] = []

    for i in range(1, args.n + 1):
        patient_id = f"SYN-{i:05d}"
        sex = rng.choice(["M", "F"])
        age = rng.randint(8, 92)
        height_cm = rng.randint(150, 195) if sex == "M" else rng.randint(145, 180)
        weight_kg = rng.randint(45, 110)
        bmi = make_bmi(height_cm, weight_kg)
        activity_level = rng.choice(ACTIVITY_LEVELS)
        comorbidities = pick_comorbidities(rng, age)

        fx_key = pick_fracture_type(rng, age)
        fx = FRACTURE_TYPES[fx_key]
        severity = rng.choices(SEVERITIES, weights=[0.5, 0.35, 0.15])[0]
        side = rng.choice(["izquierdo", "derecho"])

        is_surgical = rng.random() < fx["surgical_ratio"]
        treatment_type = "quirurgico" if is_surgical else "conservador"
        protocol_id = f"PROT-{fx_key}-{severity[0]}-{treatment_type[:3]}"

        recovery_weeks = compute_recovery_weeks(
            rng, fx["base_weeks"], age, comorbidities, activity_level, severity, bmi
        )
        outcome = compute_outcome(rng, age, comorbidities, severity)

        labs = generate_lab_results(rng, age, comorbidities, severity, treatment_type)
        lab_summary = build_lab_summary(labs)

        diagnosis_note = build_diagnosis_note(
            rng, sex, age, fx["label"], side, severity, activity_level, comorbidities, bmi, lab_summary
        )
        followup_note = build_followup_note(rng, outcome)

        image_id = f"{patient_id}.png"
        if not args.skip_images:
            make_synthetic_xray_image(IMG_DIR / image_id, seed=args.seed * 100000 + i, fracture_label=fx["label"])

        cases.append(
            PatientCase(
                patient_id=patient_id,
                age=age,
                sex=sex,
                height_cm=height_cm,
                weight_kg=weight_kg,
                bmi=bmi,
                activity_level=activity_level,
                comorbidities=";".join(comorbidities),
                fracture_type=fx_key,
                fracture_label=fx["label"],
                fracture_side=side,
                severity=severity,
                treatment_type=treatment_type,
                protocol_id=protocol_id,
                recovery_weeks=recovery_weeks,
                outcome=outcome,
                diagnosis_note=diagnosis_note,
                followup_note=followup_note,
                image_id=image_id,
                lab_summary=lab_summary,
                **labs,
            )
        )

    # patients.json
    with open(RAW_DIR / "patients.json", "w", encoding="utf-8") as f:
        json.dump([asdict(c) for c in cases], f, ensure_ascii=False, indent=2)

    # patients.csv
    with open(RAW_DIR / "patients.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(cases[0]).keys()))
        writer.writeheader()
        for c in cases:
            writer.writerow(asdict(c))

    # recovery_protocols.json: catalogo derivado combinando tipo+gravedad+tratamiento presentes en el dataset
    protocols = {}
    for c in cases:
        if c.protocol_id in protocols:
            continue
        fx = FRACTURE_TYPES[c.fracture_type]
        protocols[c.protocol_id] = {
            "protocol_id": c.protocol_id,
            "fracture_type": c.fracture_type,
            "fracture_label": fx["label"],
            "severity": c.severity,
            "treatment_type": c.treatment_type,
            "phases": [
                {"phase": "inmovilizacion", "weeks": round(fx["base_weeks"] * 0.3)},
                {"phase": "fisioterapia_fase_1_movilidad", "weeks": round(fx["base_weeks"] * 0.3)},
                {"phase": "fisioterapia_fase_2_carga_progresiva", "weeks": round(fx["base_weeks"] * 0.25)},
                {"phase": "reincorporacion_actividad", "weeks": round(fx["base_weeks"] * 0.15)},
            ],
            "typical_total_weeks_range": [
                round(fx["base_weeks"] * 0.8),
                round(fx["base_weeks"] * 1.6),
            ],
        }

    with open(RAW_DIR / "recovery_protocols.json", "w", encoding="utf-8") as f:
        json.dump(list(protocols.values()), f, ensure_ascii=False, indent=2)

    print(f"Generados {len(cases)} casos sinteticos en {RAW_DIR}")
    print(f"Generados {len(protocols)} protocolos de recuperacion")
    if not args.skip_images:
        print(f"Generadas {len(cases)} imagenes placeholder en {IMG_DIR}")


if __name__ == "__main__":
    main()

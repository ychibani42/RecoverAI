"""
Generador de dataset SINTÉTICO (100% inventado, no proviene de pacientes reales)
para prototipar el pipeline RAG de recovery-ia.

Salidas:
  data/raw/patients.json           -> casos de pacientes (estructurado + notas narrativas)
  data/raw/patients.csv            -> misma info en formato tabular
  data/raw/recovery_protocols.json -> catálogo de protocolos de recuperación por tipo/gravedad/tratamiento
  data/images/xrays/{case_id}.png  -> radiografía sintética (patrón generado, NO es una imagen
                                       médica real) usada como imagen de entrenamiento y como
                                       respaldo para los casos que no tienen una radiografía real
                                       asignada

Cuando la zona de la fractura tiene radiografías reales disponibles en
data/images/xrays_reales/ (ver manifest_fuentes.json), una parte de los casos
las usa como imagen principal (imagen_radiografia_tipo="real"); el resto usa
la radiografía sintética generada aquí (imagen_radiografia_tipo="sintetica").

Uso:
  py scripts/generate_synthetic_data.py --n 300 --seed 42
"""

import argparse
import csv
import json
import random
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
IMAGES_DIR = ROOT / "data" / "images"
SYNTHETIC_IMG_DIR = IMAGES_DIR / "xrays"
REAL_IMG_DIR = IMAGES_DIR / "xrays_reales"
REAL_MANIFEST_PATH = REAL_IMG_DIR / "manifest_fuentes.json"

FRACTURE_TYPES = {
    "muneca_colles": {
        "label": "Fractura de radio distal (tipo Colles)",
        "zona": "Muneca/Radio",
        "base_weeks": 7,
        "surgical_ratio": 0.35,
        "real_zone": "muneca_radio",
        "conservative_care": "inmovilizacion con yeso/ferula",
    },
    "humero_diafisis": {
        "label": "Fractura de diáfisis humeral",
        "zona": "Humero/Diafisis",
        "base_weeks": 10,
        "surgical_ratio": 0.4,
        "real_zone": None,
        "conservative_care": "inmovilizacion con cabestrillo",
    },
    "femur_diafisis": {
        "label": "Fractura de diáfisis femoral",
        "zona": "Femur/Diafisis",
        "base_weeks": 14,
        "surgical_ratio": 0.9,
        "real_zone": None,
        "conservative_care": "descarga progresiva con apoyo de muletas",
    },
    "cadera_cuello_femoral": {
        "label": "Fractura de cuello femoral (cadera)",
        "zona": "Cadera/Cuello femoral",
        "base_weeks": 14,
        "surgical_ratio": 0.85,
        "real_zone": None,
        "conservative_care": "descarga progresiva con apoyo de muletas",
    },
    "tibia_perone": {
        "label": "Fractura de tibia y peroné",
        "zona": "Tibia/Perone",
        "base_weeks": 13,
        "surgical_ratio": 0.55,
        "real_zone": None,
        "conservative_care": "inmovilizacion con yeso/ferula",
    },
    "tobillo_maleolar": {
        "label": "Fractura maleolar de tobillo",
        "zona": "Tobillo",
        "base_weeks": 8,
        "surgical_ratio": 0.3,
        "real_zone": "tobillo",
        "conservative_care": "inmovilizacion con yeso/ferula",
    },
    "clavicula": {
        "label": "Fractura de clavícula",
        "zona": "Clavicula",
        "base_weeks": 6,
        "surgical_ratio": 0.15,
        "real_zone": None,
        "conservative_care": "inmovilizacion con cabestrillo",
    },
    "vertebral_compresion": {
        "label": "Fractura vertebral por compresión",
        "zona": "Columna vertebral",
        "base_weeks": 10,
        "surgical_ratio": 0.2,
        "real_zone": None,
        "conservative_care": "ortesis (corse) y reposo relativo",
    },
    "costilla": {
        "label": "Fractura costal",
        "zona": "Costillas",
        "base_weeks": 5,
        "surgical_ratio": 0.02,
        "real_zone": None,
        "conservative_care": "analgesia y control respiratorio, sin inmovilizacion rigida",
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
SEVERITY_TO_GRAVEDAD = {"I - simple": "leve", "II - desplazada": "moderada", "III - conminuta": "grave"}

ACTIVITY_LEVELS = ["sedentario", "moderado", "deportista"]
COMORBIDITIES_POOL = ["diabetes", "osteoporosis", "hipertension", "tabaquismo", "obesidad"]

MECANISMOS_LESION = [
    "caida accidental",
    "accidente de trafico",
    "sobrecarga por actividad repetitiva",
    "caida desde altura",
    "traumatismo directo durante actividad deportiva",
    "caida en el hogar",
]

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
    case_id: str
    uuid: str
    sexo: str
    edad: int
    altura_cm: int
    peso_kg: float
    imc: float
    nivel_actividad: str
    deportista: bool
    comorbilidades: list[str]
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
    hitos_recuperacion: list[dict]
    complicaciones: str
    puntuacion_resultado: float
    imagen_radiografia: str
    imagen_radiografia_tipo: str
    imagen_radiografia_fuente: str
    imagen_radiografia_sintetica_original: str | None = None


def make_bmi(height_cm: int, weight_kg: float) -> float:
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
    return chosen if chosen else ["ninguna relevante"]


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


def compute_puntuacion_resultado(rng: random.Random, outcome: str) -> float:
    if outcome == "complicacion":
        return round(rng.uniform(20, 54), 1)
    if outcome == "recuperacion_parcial_con_limitacion":
        return round(rng.uniform(55, 84), 1)
    return round(rng.uniform(85, 100), 1)


def build_diagnostico_texto(sexo: str, edad: int, fractura_tipo: str, imc: float,
                             nivel_actividad: str, mecanismo_lesion: str,
                             comorbilidades: list[str]) -> str:
    genero = "hombre" if sexo == "Hombre" else "mujer"
    comorb_txt = ", ".join(comorbilidades)
    return (
        f"{fractura_tipo} en paciente {genero} de {edad} anhos, IMC {imc}, "
        f"nivel de actividad {nivel_actividad}. Mecanismo: {mecanismo_lesion}. "
        f"Comorbilidades: {comorb_txt}."
    )


def build_hallazgos_imagen_texto(fractura_tipo: str, fractura_zona: str, gravedad: str,
                                  semanas_recuperacion_total: int) -> str:
    desplazamiento = "sin" if gravedad == "leve" else "con"
    return (
        f"Radiografia simple en proyecciones AP y lateral que confirma {fractura_tipo.lower()} "
        f"a nivel de {fractura_zona.lower()}, {desplazamiento} desplazamiento significativo "
        f"segun gravedad clasificada como '{gravedad}'. Control evolutivo a las 2, 6 y 12 semanas."
    )


def build_plan_recuperacion_texto(tratamiento_detalle: str, semanas_estabilizacion: int,
                                   semanas_fisioterapia: int, complicaciones: str) -> str:
    return (
        f"Tratamiento: {tratamiento_detalle}. Fase de estabilizacion de {semanas_estabilizacion} "
        f"semanas seguida de progresion de fisioterapia de {semanas_fisioterapia} semanas "
        "(movilizacion activa asistida, fortalecimiento progresivo y reincorporacion funcional). "
        f"Complicaciones registradas: {complicaciones}."
    )


def build_hitos_recuperacion(semanas_estabilizacion: int, semanas_recuperacion_total: int) -> list[dict]:
    return [
        {"semana": 2, "hito": "primer control radiografico, retirada/ajuste de inmovilizacion parcial"},
        {"semana": semanas_estabilizacion, "hito": "consolidacion clinica/radiologica inicial, inicio de carga progresiva"},
        {"semana": semanas_recuperacion_total, "hito": "alta funcional o reincorporacion a actividad habitual"},
    ]


def build_complicaciones(rng: random.Random, outcome: str) -> str:
    if outcome == "complicacion":
        return rng.choice(COMPLICATION_PHRASES)
    return "ninguna"


def make_synthetic_xray_image(path: Path, seed: int, size: int = 256) -> None:
    """Genera una imagen sintetica (patron generado, no una radiografia real)
    para el pipeline de embeddings de imagen y como respaldo cuando no hay
    una radiografia real disponible para la zona."""
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


def load_real_images_manifest() -> dict:
    if not REAL_MANIFEST_PATH.is_file():
        return {}
    return json.loads(REAL_MANIFEST_PATH.read_text(encoding="utf-8"))


def pick_image(rng: random.Random, fx: dict, case_id: str, manifest: dict) -> dict:
    """Elige la radiografia del caso: real (si hay disponibles para la zona,
    con un 40% de probabilidad) o sintetica en su defecto. La sintetica
    siempre se genera y se guarda, ya sea como imagen principal o como
    'original' de respaldo de un caso con imagen real."""
    real_zone = fx["real_zone"]
    real_entries = manifest.get(real_zone, []) if real_zone else []

    synthetic_rel_path = f"xrays/{case_id}.png"

    if real_entries and rng.random() < 0.4:
        entry = rng.choice(real_entries)
        return {
            "imagen_radiografia": f"xrays_reales/{entry['archivo']}",
            "imagen_radiografia_sintetica_original": synthetic_rel_path,
            "imagen_radiografia_tipo": "real",
            "imagen_radiografia_fuente": (
                "Radiografia real anonimizada de un dataset publico de rayos X. Reutilizada "
                "entre varios casos sinteticos de la misma zona: no corresponde en exclusiva a "
                "este paciente sintetico, solo ilustra el tipo de lesion de forma realista."
            ),
        }

    return {
        "imagen_radiografia": synthetic_rel_path,
        "imagen_radiografia_sintetica_original": None,
        "imagen_radiografia_tipo": "sintetica",
        "imagen_radiografia_fuente": (
            "Radiografia sintetica generada proceduralmente (no hay imagenes reales "
            "identificables para esta zona en el dataset disponible)."
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=300, help="numero de casos sinteticos a generar")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--skip-images", action="store_true", help="no generar imagenes sinteticas")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    SYNTHETIC_IMG_DIR.mkdir(parents=True, exist_ok=True)
    manifest = load_real_images_manifest()

    cases: list[PatientCase] = []

    for i in range(1, args.n + 1):
        case_id = f"CASE-{i:04d}"
        sexo = rng.choice(["Hombre", "Mujer"])
        edad = rng.randint(8, 92)
        altura_cm = rng.randint(150, 195) if sexo == "Hombre" else rng.randint(145, 180)
        peso_kg = float(rng.randint(45, 110))
        imc = make_bmi(altura_cm, peso_kg)
        nivel_actividad = rng.choice(ACTIVITY_LEVELS)
        deportista = nivel_actividad == "deportista"
        comorbilidades = pick_comorbidities(rng, edad)
        mecanismo_lesion = rng.choice(MECANISMOS_LESION)

        fx_key = pick_fracture_type(rng, edad)
        fx = FRACTURE_TYPES[fx_key]
        severity = rng.choices(SEVERITIES, weights=[0.5, 0.35, 0.15])[0]
        gravedad = SEVERITY_TO_GRAVEDAD[severity]

        is_surgical = rng.random() < fx["surgical_ratio"]
        tratamiento = "quirurgico" if is_surgical else "conservador"
        tratamiento_detalle = (
            "reduccion abierta y fijacion interna con control radiografico postoperatorio periodico"
            if is_surgical
            else f"{fx['conservative_care']} y control radiografico periodico"
        )

        semanas_recuperacion_total = compute_recovery_weeks(
            rng, fx["base_weeks"], edad, comorbilidades, nivel_actividad, severity, imc
        )
        semanas_estabilizacion = max(2, round(semanas_recuperacion_total * 0.4))
        semanas_fisioterapia = max(1, semanas_recuperacion_total - semanas_estabilizacion)

        outcome = compute_outcome(rng, edad, comorbilidades, severity)
        complicaciones = build_complicaciones(rng, outcome)
        puntuacion_resultado = compute_puntuacion_resultado(rng, outcome)

        diagnostico_texto = build_diagnostico_texto(
            sexo, edad, fx["label"], imc, nivel_actividad, mecanismo_lesion, comorbilidades
        )
        hallazgos_imagen_texto = build_hallazgos_imagen_texto(
            fx["label"], fx["zona"], gravedad, semanas_recuperacion_total
        )
        plan_recuperacion_texto = build_plan_recuperacion_texto(
            tratamiento_detalle, semanas_estabilizacion, semanas_fisioterapia, complicaciones
        )
        hitos_recuperacion = build_hitos_recuperacion(semanas_estabilizacion, semanas_recuperacion_total)

        image_info = pick_image(rng, fx, case_id, manifest)
        if not args.skip_images:
            make_synthetic_xray_image(SYNTHETIC_IMG_DIR / f"{case_id}.png", seed=args.seed * 100000 + i)

        cases.append(
            PatientCase(
                case_id=case_id,
                uuid=str(uuid.uuid4()),
                sexo=sexo,
                edad=edad,
                altura_cm=altura_cm,
                peso_kg=peso_kg,
                imc=imc,
                nivel_actividad=nivel_actividad,
                deportista=deportista,
                comorbilidades=comorbilidades,
                fractura_tipo=fx["label"],
                fractura_zona=fx["zona"],
                gravedad=gravedad,
                mecanismo_lesion=mecanismo_lesion,
                tratamiento=tratamiento,
                tratamiento_detalle=tratamiento_detalle,
                diagnostico_texto=diagnostico_texto,
                hallazgos_imagen_texto=hallazgos_imagen_texto,
                plan_recuperacion_texto=plan_recuperacion_texto,
                semanas_recuperacion_total=semanas_recuperacion_total,
                semanas_estabilizacion=semanas_estabilizacion,
                semanas_fisioterapia=semanas_fisioterapia,
                hitos_recuperacion=hitos_recuperacion,
                complicaciones=complicaciones,
                puntuacion_resultado=puntuacion_resultado,
                **image_info,
            )
        )

    # patients.json (omite imagen_radiografia_sintetica_original cuando no aplica, en vez de null)
    records = []
    for c in cases:
        record = asdict(c)
        if record["imagen_radiografia_sintetica_original"] is None:
            del record["imagen_radiografia_sintetica_original"]
        records.append(record)

    with open(RAW_DIR / "patients.json", "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    # patients.csv
    fieldnames = list(asdict(cases[0]).keys())
    with open(RAW_DIR / "patients.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for c in cases:
            writer.writerow(asdict(c))

    # recovery_protocols.json: catalogo derivado combinando tipo+gravedad+tratamiento presentes en el dataset
    protocols = {}
    for c in cases:
        protocol_id = f"PROT-{c.fractura_tipo}-{c.gravedad}-{c.tratamiento}"
        if protocol_id in protocols:
            continue
        fx = next(v for v in FRACTURE_TYPES.values() if v["label"] == c.fractura_tipo)
        protocols[protocol_id] = {
            "protocol_id": protocol_id,
            "fractura_tipo": c.fractura_tipo,
            "fractura_zona": c.fractura_zona,
            "gravedad": c.gravedad,
            "tratamiento": c.tratamiento,
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
        print(f"Generadas {len(cases)} imagenes sinteticas en {SYNTHETIC_IMG_DIR}")


if __name__ == "__main__":
    main()

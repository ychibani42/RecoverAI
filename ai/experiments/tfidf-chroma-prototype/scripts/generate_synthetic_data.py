#!/usr/bin/env python3
"""
Generador de datos sinteticos de pacientes de traumatologia/ortopedia
para el hackathon de "busqueda de casos similares" (RAG).

IMPORTANTE: Todos los datos son FICTICIOS, generados aleatoriamente.
No representan pacientes reales. Sirven para prototipar el pipeline
(indexacion + busqueda vectorial + agente) antes de conectar datos
reales del hospital bajo los controles de HIPAA/RGPD correspondientes.

Uso:
    python3 generate_synthetic_data.py --n 300 --seed 42 --out ../data/patients.json
"""

import argparse
import json
import random
import uuid
from pathlib import Path

random.seed(0)

SEXOS = ["Hombre", "Mujer"]

FRACTURAS = [
    # (nombre, hueso/zona, gravedad tipica, semanas_base_recuperacion)
    ("Fractura de humero (diafisaria)", "Humero", "moderada", 10),
    ("Fractura de humero (cuello quirurgico)", "Humero proximal", "moderada", 9),
    ("Fractura de radio distal (Colles)", "Muneca/Radio", "leve", 6),
    ("Fractura de cuello femoral", "Cadera/Femur", "grave", 16),
    ("Fractura pertrocanterea de cadera", "Cadera", "grave", 14),
    ("Fractura de tobillo bimaleolar", "Tobillo", "moderada", 8),
    ("Fractura de tibia (diafisaria)", "Tibia", "grave", 14),
    ("Fractura de tibia y perone", "Tibia/Perone", "grave", 15),
    ("Fractura de clavicula", "Clavicula", "leve", 6),
    ("Fractura vertebral por compresion (osteoporotica)", "Columna lumbar", "moderada", 12),
    ("Fractura de escafoides", "Muneca/Escafoides", "moderada", 10),
    ("Fractura de calcaneo", "Pie/Calcaneo", "grave", 12),
    ("Fractura de rotula", "Rodilla/Rotula", "moderada", 9),
    ("Fractura de meseta tibial", "Rodilla/Tibia proximal", "grave", 13),
    ("Fractura de falange (mano)", "Mano", "leve", 4),
]

MECANISMOS = [
    "caida accidental desde propia altura",
    "caida en la via publica",
    "accidente deportivo",
    "accidente de trafico (baja energia)",
    "accidente de trafico (alta energia)",
    "caida desde escalera",
    "accidente laboral",
    "caida en pista de esqui",
    "sobrecarga por actividad repetitiva",
    "caida durante practica de ciclismo",
]

TRATAMIENTOS_CONSERVADORES = [
    "inmovilizacion con yeso/ferula y control radiografico periodico",
    "ortesis funcional con carga progresiva segun tolerancia",
    "reposo relativo, analgesia pautada y fisioterapia diferida",
]

TRATAMIENTOS_QUIRURGICOS = [
    "reduccion abierta y fijacion interna (placa y tornillos)",
    "enclavado endomedular",
    "fijacion con tornillos canulados",
    "artroplastia parcial de cadera",
    "fijacion externa temporal seguida de osteosintesis definitiva",
    "reduccion cerrada percutanea con agujas de Kirschner",
]

COMPLICACIONES = [
    "ninguna",
    "ninguna",
    "ninguna",
    "retraso de consolidacion leve",
    "rigidez articular residual",
    "infeccion superficial de herida quirurgica (resuelta con antibioterapia)",
    "sindrome doloroso regional complejo leve",
    "necesidad de retirada de material de osteosintesis",
]

NIVELES_ACTIVIDAD = ["sedentario", "moderadamente activo", "activo", "deportista federado"]


def bmi(peso, altura_cm):
    h = altura_cm / 100
    return round(peso / (h * h), 1)


def generar_paciente(idx: int) -> dict:
    sexo = random.choice(SEXOS)
    edad = random.choices(
        population=range(18, 95),
        weights=[1 if e < 50 else (2 if e < 70 else 3) for e in range(18, 95)],
        k=1,
    )[0]

    altura = round(random.gauss(170 if sexo == "Hombre" else 160, 7))
    altura = max(145, min(200, altura))
    peso = round(random.gauss(78 if sexo == "Hombre" else 66, 13), 1)
    peso = max(45, min(140, peso))
    imc = bmi(peso, altura)

    nivel_actividad = random.choice(NIVELES_ACTIVIDAD)
    deportista = nivel_actividad == "deportista federado"

    nombre_fx, zona, gravedad, semanas_base = random.choice(FRACTURAS)
    mecanismo = random.choice(MECANISMOS)

    # Comorbilidades mas probables con la edad
    posibles_comorb = []
    if edad > 60:
        posibles_comorb += ["osteoporosis", "hipertension arterial", "diabetes mellitus tipo 2"]
    if imc >= 30:
        posibles_comorb += ["obesidad"]
    if edad > 70:
        posibles_comorb += ["deterioro cognitivo leve"]
    comorbilidades = sorted(set(random.sample(posibles_comorb, k=min(len(posibles_comorb), random.choice([0, 0, 1, 1, 2])))))
    if not comorbilidades:
        comorbilidades = ["ninguna relevante"]

    quirurgico = gravedad in ("moderada", "grave") and random.random() < (0.55 if gravedad == "moderada" else 0.85)
    tratamiento = random.choice(TRATAMIENTOS_QUIRURGICOS) if quirurgico else random.choice(TRATAMIENTOS_CONSERVADORES)

    # Duracion de recuperacion ajustada por edad, comorbilidades e IMC
    factor_edad = 1 + max(0, (edad - 50)) * 0.01
    factor_comorb = 1 + (0.08 * (len(comorbilidades) if comorbilidades != ["ninguna relevante"] else 0))
    factor_imc = 1 + (0.05 if imc >= 30 else 0)
    semanas_totales = round(semanas_base * factor_edad * factor_comorb * factor_imc)
    semanas_estabilizacion = max(2, round(semanas_totales * 0.35))
    semanas_fisioterapia = max(2, semanas_totales - semanas_estabilizacion)

    complicacion = random.choices(COMPLICACIONES, weights=[5, 5, 5, 2, 2, 1, 1, 1], k=1)[0]

    puntuacion_resultado = round(
        max(40, min(100, random.gauss(88 if complicacion == "ninguna" else 72, 8))), 0
    )

    diagnostico = (
        f"{nombre_fx} en paciente {sexo.lower()} de {edad} anhos, IMC {imc}, "
        f"nivel de actividad {nivel_actividad}. Mecanismo: {mecanismo}. "
        f"Comorbilidades: {', '.join(comorbilidades)}."
    )

    hallazgos_imagen = (
        f"Radiografia simple en proyecciones AP y lateral que confirma {nombre_fx.lower()} "
        f"a nivel de {zona.lower()}, sin/con desplazamiento significativo segun gravedad "
        f"clasificada como '{gravedad}'. Control evolutivo a las 2, 6 y 12 semanas."
    )

    plan_recuperacion = (
        f"Tratamiento: {tratamiento}. Fase de estabilizacion de {semanas_estabilizacion} semanas "
        f"seguida de progresion de fisioterapia de {semanas_fisioterapia} semanas "
        f"(movilizacion activa asistida, fortalecimiento progresivo y reincorporacion funcional). "
        f"Complicaciones registradas: {complicacion}."
    )

    hitos = [
        {"semana": 2, "hito": "primer control radiografico, retirada/ajuste de inmovilizacion parcial"},
        {"semana": semanas_estabilizacion, "hito": "consolidacion clinica/radiologica inicial, inicio de carga progresiva"},
        {"semana": semanas_totales, "hito": "alta funcional o reincorporacion a actividad habitual"},
    ]

    return {
        "case_id": f"CASE-{idx:04d}",
        "uuid": str(uuid.uuid4()),
        "sexo": sexo,
        "edad": edad,
        "altura_cm": altura,
        "peso_kg": peso,
        "imc": imc,
        "nivel_actividad": nivel_actividad,
        "deportista": deportista,
        "fractura_tipo": nombre_fx,
        "fractura_zona": zona,
        "gravedad": gravedad,
        "mecanismo_lesion": mecanismo,
        "comorbilidades": comorbilidades,
        "tratamiento": "quirurgico" if quirurgico else "conservador",
        "tratamiento_detalle": tratamiento,
        "diagnostico_texto": diagnostico,
        "hallazgos_imagen_texto": hallazgos_imagen,
        "plan_recuperacion_texto": plan_recuperacion,
        "semanas_recuperacion_total": semanas_totales,
        "semanas_estabilizacion": semanas_estabilizacion,
        "semanas_fisioterapia": semanas_fisioterapia,
        "hitos_recuperacion": hitos,
        "complicaciones": complicacion,
        "puntuacion_resultado": puntuacion_resultado,
    }


def main():
    parser = argparse.ArgumentParser(description="Genera pacientes sinteticos de ortopedia")
    parser.add_argument("--n", type=int, default=300, help="numero de casos a generar")
    parser.add_argument("--seed", type=int, default=42, help="semilla aleatoria")
    parser.add_argument("--out", type=str, default="../data/patients.json", help="ruta de salida (json)")
    args = parser.parse_args()

    random.seed(args.seed)
    pacientes = [generar_paciente(i + 1) for i in range(args.n)]

    out_path = Path(__file__).parent / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(pacientes, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Generados {len(pacientes)} casos sinteticos -> {out_path.resolve()}")


if __name__ == "__main__":
    main()

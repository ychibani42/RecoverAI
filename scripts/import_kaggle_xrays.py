"""Organiza el dataset de Kaggle "Bone Fracture Multi-Region X-ray Data" (o
cualquier otro dataset de rayos X con estructura similar) descargado a mano en
data/kaggle_raw/, clasificando las imagenes FRACTURADAS por region anatomica
(cuando el nombre de carpeta/archivo lo permite deducir) dentro de
data/xray_images/<fracture_type>/, con una bolsa generica data/xray_images/generic/
para las que no se puedan clasificar.

Estas imagenes sustituyen al placeholder sintetico (patron generado) como
radiografia real de apoyo visual; los datos clinicos del paciente (edad, IMC,
comorbilidades, analitica, resultado) siguen siendo sinteticos/anonimizados,
ya que este dataset no trae informacion de paciente, solo imagen + fracturado
o no.

Uso:
  uv run scripts/import_kaggle_xrays.py
"""

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "data" / "kaggle_raw"
DEST_DIR = ROOT / "data" / "xray_images"

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp"}

NOT_FRACTURED_MARKERS = ["not fractured", "not_fractured", "non fractured", "non_fractured", "normal", "healthy"]
FRACTURED_MARKERS = ["fractured", "fracture"]

REGION_KEYWORDS = {
    "muneca_colles": ["wrist", "radius", "colles"],
    "humero_diafisis": ["humerus", "shoulder", "arm"],
    "femur_diafisis": ["femur", "thigh"],
    "cadera_cuello_femoral": ["hip", "pelvis"],
    "tibia_perone": ["tibia", "fibula", "shin", "leg", "knee"],
    "tobillo_maleolar": ["ankle", "foot"],
    "clavicula": ["clavicle", "collarbone"],
    "vertebral_compresion": ["spine", "vertebra", "lumbar", "spinal"],
    "costilla": ["rib", "chest", "thorax"],
}


def is_fractured(path_str: str) -> bool:
    lower = path_str.lower()
    if any(marker in lower for marker in NOT_FRACTURED_MARKERS):
        return False
    return any(marker in lower for marker in FRACTURED_MARKERS)


def classify_region(path_str: str) -> str:
    lower = path_str.lower()
    for fracture_type, keywords in REGION_KEYWORDS.items():
        if any(keyword in lower for keyword in keywords):
            return fracture_type
    return "generic"


def main():
    if not SRC_DIR.exists() or not any(SRC_DIR.iterdir()):
        print(f"No hay nada que importar en {SRC_DIR}. Lee data/kaggle_raw/README.md.")
        return

    counts: dict[str, int] = {}
    skipped_not_fractured = 0
    skipped_other = 0

    for path in SRC_DIR.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue

        rel = str(path.relative_to(SRC_DIR))

        if not is_fractured(rel):
            skipped_not_fractured += 1
            continue

        fracture_type = classify_region(rel)
        dest_dir = DEST_DIR / fracture_type
        dest_dir.mkdir(parents=True, exist_ok=True)

        dest_path = dest_dir / path.name
        if dest_path.exists():
            dest_path = dest_dir / f"{path.stem}_{counts.get(fracture_type, 0)}{path.suffix}"

        shutil.copy2(path, dest_path)
        counts[fracture_type] = counts.get(fracture_type, 0) + 1

    if not counts:
        print(
            "No se encontro ninguna imagen clasificable como 'fracturada' en "
            f"{SRC_DIR}. Comprueba que la estructura de carpetas coincide con la "
            "del dataset (train/val/test > Fractured / Not Fractured)."
        )
        return

    print(f"Importadas {sum(counts.values())} imagenes en {DEST_DIR}:")
    for fracture_type, n in sorted(counts.items()):
        print(f"  - {fracture_type}: {n}")
    print(f"Descartadas por 'no fracturadas': {skipped_not_fractured}")
    if skipped_other:
        print(f"Descartadas por no reconocidas: {skipped_other}")
    if counts.get("generic", 0) == sum(counts.values()):
        print(
            "\nAviso: ninguna imagen pudo clasificarse por region anatomica "
            "(todas cayeron en 'generic'). Es normal si el dataset solo distingue "
            "Fractured/Not Fractured sin indicar la region en la ruta del archivo."
        )


if __name__ == "__main__":
    main()

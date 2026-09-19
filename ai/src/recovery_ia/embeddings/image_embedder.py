"""Embedder de imagen para radiografias.

Pendiente de decision: modelo de vision especializado en radiologia (p.ej. un
checkpoint de tipo BiomedCLIP) frente a un CLIP generico. El dataset de
entrenamiento vive en data/images/xrays/ (radiografias sinteticas a escala) y
el de evaluacion en data/images/xrays_reales/ (radiografias reales); la
eleccion real de modelo se hace al integrar y validar contra estas imagenes.
"""

from pathlib import Path


def embed_image(image_path: Path) -> list[float]:
    raise NotImplementedError(
        "Pendiente de elegir e integrar el modelo de embeddings de imagen "
        "(ver docstring del modulo)."
    )

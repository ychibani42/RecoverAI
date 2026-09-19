"""Embedder de imagen para radiografias.

Pendiente de decision: modelo de vision especializado en radiologia (p.ej. un
checkpoint de tipo BiomedCLIP) frente a un CLIP generico. Con el dataset
sintetico actual (data/images/*.png son placeholders, no radiografias reales)
cualquier backbone de vision sirve para probar el pipeline end-to-end; la
eleccion real de modelo se hace al integrar imagenes clinicas reales.
"""

from pathlib import Path


def embed_image(image_path: Path) -> list[float]:
    raise NotImplementedError(
        "Pendiente de elegir e integrar el modelo de embeddings de imagen "
        "(ver docstring del modulo)."
    )

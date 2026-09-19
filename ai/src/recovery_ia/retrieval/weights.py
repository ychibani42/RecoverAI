"""Pesos estaticos de los factores estructurados usados para re-rankear los
casos similares y para indicarle al LLM que factores deben pesar mas en su
razonamiento clinico (p.ej. a mayor edad, mas peso al reposo prolongado)."""

FIELD_WEIGHTS: dict[str, float] = {
    "edad": 0.9,
    "gravedad": 0.8,
    "comorbilidades": 0.7,
    "imc": 0.6,
    "nivel_actividad": 0.5,
    "deportista": 0.4,
}

# Rango usado para normalizar la diferencia de edad/IMC a [0, 1].
EDAD_RANGO = 40.0
IMC_RANGO = 20.0

# Escalas ordinales: distancia normalizada entre categorias segun su indice.
GRAVEDAD_ORDEN = ["leve", "moderada", "grave"]
NIVEL_ACTIVIDAD_ORDEN = ["sedentario", "moderado", "activo"]


def _ordinal_distance(valor_a: str, valor_b: str, orden: list[str]) -> float:
    try:
        idx_a = orden.index(valor_a)
        idx_b = orden.index(valor_b)
    except ValueError:
        return 1.0 if valor_a != valor_b else 0.0
    return abs(idx_a - idx_b) / (len(orden) - 1)


def _comorbilidades_distance(lista_a: list[str], lista_b: list[str]) -> float:
    set_a, set_b = set(lista_a), set(lista_b)
    if not set_a and not set_b:
        return 0.0
    union = set_a | set_b
    interseccion = set_a & set_b
    return 1.0 - (len(interseccion) / len(union))


def field_distance(field: str, valor_paciente, valor_caso) -> float:
    """Distancia normalizada [0, 1] entre el valor del paciente nuevo y el
    de un caso historico para un campo estructurado ponderado."""
    if field == "edad":
        return min(abs(valor_paciente - valor_caso) / EDAD_RANGO, 1.0)
    if field == "imc":
        return min(abs(valor_paciente - valor_caso) / IMC_RANGO, 1.0)
    if field == "gravedad":
        return _ordinal_distance(valor_paciente, valor_caso, GRAVEDAD_ORDEN)
    if field == "nivel_actividad":
        return _ordinal_distance(valor_paciente, valor_caso, NIVEL_ACTIVIDAD_ORDEN)
    if field == "deportista":
        return 0.0 if bool(valor_paciente) == bool(valor_caso) else 1.0
    if field == "comorbilidades":
        return _comorbilidades_distance(valor_paciente or [], valor_caso or [])
    raise ValueError(f"Campo sin distancia definida: {field}")

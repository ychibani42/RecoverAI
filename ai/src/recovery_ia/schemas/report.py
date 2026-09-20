from pydantic import BaseModel, Field

from .query import SimilarCaseResult


class FactorJustificacion(BaseModel):
    """Explica como un factor ponderado del paciente (edad, gravedad...)
    influyo en la recomendacion, para que el clinico vea el razonamiento."""

    factor: str = Field(description="Nombre del factor ponderado (ej. 'edad', 'gravedad').")
    valor_paciente: str = Field(description="Valor de ese factor en el paciente nuevo.")
    peso: float = Field(description="Peso asignado a ese factor (0-1), mayor = mas influyente.")
    justificacion: str = Field(
        description="Por que este valor del factor, dado su peso, influyo en la recomendacion "
        "(ej. 'edad alta (72) con peso 0.9: se prioriza un periodo de reposo mas prolongado'). Marca en "
        "**negrita** (Markdown, doble asterisco) el dato o conclusion mas relevante de la frase."
    )


class ClinicalReport(BaseModel):
    """Informe final que devuelve el sistema para un paciente nuevo, generado
    por el LLM a partir de los casos similares recuperados de Qdrant."""

    resumen_casos_similares: str = Field(
        description="Resumen de los casos historicos similares encontrados y por que se parecen al caso "
        "consultado. Marca en **negrita** (Markdown, doble asterisco) las 1-3 frases o datos mas "
        "relevantes clinicamente; no pongas en negrita el texto completo."
    )
    tratamiento_recomendado: str = Field(
        description="Tratamiento sugerido (conservador o quirurgico, con detalles) basado en los casos "
        "similares. Marca en **negrita** (Markdown, doble asterisco) las 1-3 frases o datos mas relevantes "
        "clinicamente (p. ej. el tratamiento elegido); no pongas en negrita el texto completo."
    )
    tiempo_recuperacion_estimado: str = Field(
        description="Rango de semanas estimado hasta la recuperacion, segun los casos similares. Marca en "
        "**negrita** (Markdown, doble asterisco) el rango de semanas."
    )
    semanas_hasta_revision: int = Field(
        description="Numero entero de semanas hasta la cita de revision recomendada, coherente con "
        "tiempo_recuperacion_estimado (ej. si la recuperacion es de 6-8 semanas, un valor razonable es 6, 7 u 8)."
    )
    dieta_recomendada: str | None = Field(
        default=None,
        description="Recomendaciones dieteticas solo si son relevantes (consolidacion osea, comorbilidades "
        "como diabetes u obesidad); null si no aplica. Marca en **negrita** (Markdown, doble asterisco) las "
        "1-3 frases o datos mas relevantes clinicamente; no pongas en negrita el texto completo.",
    )
    habitos_salud_recomendados: str | None = Field(
        default=None,
        description="Habitos recomendados durante la recuperacion: actividad fisica, tabaco/alcohol, "
        "adherencia a fisioterapia, etc. Marca en **negrita** (Markdown, doble asterisco) las 1-3 frases o "
        "datos mas relevantes clinicamente; no pongas en negrita el texto completo.",
    )
    advertencia: str = Field(
        description="Aviso de que es una orientacion de apoyo a la decision y no sustituye el criterio "
        "clinico del profesional ni constituye un diagnostico. Marca en **negrita** (Markdown, doble "
        "asterisco) la parte mas critica del aviso."
    )
    factores_clave: list[FactorJustificacion] = Field(
        default=[],
        description="Factores ponderados del paciente nuevo (edad, gravedad, comorbilidades, IMC, "
        "nivel de actividad, deportista) que mas influyeron en la recomendacion, con justificacion "
        "de por que ese valor, dado su peso, importa para este caso.",
    )


class ReportResponse(BaseModel):
    """Respuesta completa del endpoint /cases/report: el informe clinico junto con
    los casos similares recuperados de Qdrant en los que se basa, para poder
    mostrarlos en la UI (mapa de vecinos mas proximos)."""

    report: ClinicalReport
    similar_cases: list[SimilarCaseResult]

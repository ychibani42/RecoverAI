from pydantic import BaseModel, Field


class ClinicalReport(BaseModel):
    """Informe final que devuelve el sistema para un paciente nuevo, generado
    por el LLM a partir de los casos similares recuperados de Qdrant."""

    resumen_casos_similares: str = Field(
        description="Resumen de los casos historicos similares encontrados y por que se parecen al caso consultado."
    )
    tratamiento_recomendado: str = Field(
        description="Tratamiento sugerido (conservador o quirurgico, con detalles) basado en los casos similares."
    )
    tiempo_recuperacion_estimado: str = Field(
        description="Rango de semanas estimado hasta la recuperacion, segun los casos similares."
    )
    dieta_recomendada: str | None = Field(
        default=None,
        description="Recomendaciones dieteticas solo si son relevantes (consolidacion osea, comorbilidades "
        "como diabetes u obesidad); null si no aplica.",
    )
    habitos_salud_recomendados: str | None = Field(
        default=None,
        description="Habitos recomendados durante la recuperacion: actividad fisica, tabaco/alcohol, "
        "adherencia a fisioterapia, etc.",
    )
    advertencia: str = Field(
        description="Aviso de que es una orientacion de apoyo a la decision y no sustituye el criterio "
        "clinico del profesional ni constituye un diagnostico."
    )

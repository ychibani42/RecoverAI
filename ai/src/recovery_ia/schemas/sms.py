from datetime import datetime

from pydantic import BaseModel, Field


class SmsAppointmentRequest(BaseModel):
    """Peticion para programar el SMS de una cita: confirmacion inmediata mas
    recordatorios el dia anterior y el mismo dia de la cita."""

    phone: str = Field(description="Telefono del paciente en formato internacional, ej. 34600111222")
    weeks: int = Field(ge=0, le=52, description="Semanas desde hoy hasta la cita")


class SmsAppointmentResponse(BaseModel):
    appointment_date: datetime
    scheduled: list[str]

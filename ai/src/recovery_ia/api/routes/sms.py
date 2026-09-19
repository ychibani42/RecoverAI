from fastapi import APIRouter

from recovery_ia.schemas import SmsAppointmentRequest, SmsAppointmentResponse
from recovery_ia.sms import schedule_appointment_sms

router = APIRouter(prefix="/sms", tags=["sms"])


@router.post("/appointment", response_model=SmsAppointmentResponse)
def schedule_appointment(payload: SmsAppointmentRequest) -> SmsAppointmentResponse:
    """Envia por SMS la confirmacion de la cita (hoy + payload.weeks semanas) y
    programa los recordatorios del dia anterior y del mismo dia de la cita."""
    appointment_date = schedule_appointment_sms(payload.phone, payload.weeks)
    return SmsAppointmentResponse(appointment_date=appointment_date, scheduled=["confirmation", "day_before", "same_day"])

from datetime import datetime, timedelta, timezone

from recovery_ia.storage import get_sms_reminders_collection

from .vonage_client import send_sms


def _format_date(dt: datetime) -> str:
    return dt.strftime("%d/%m/%Y")


def _message_for(kind: str, appointment_date: datetime) -> str:
    date_str = _format_date(appointment_date)
    if kind == "confirmation":
        return f"Recover IA: su cita de revision ha sido programada para el {date_str}."
    if kind == "day_before":
        return f"Recover IA: recordatorio, su cita de revision es manana {date_str}."
    return f"Recover IA: recordatorio, su cita de revision es hoy {date_str}."


def schedule_appointment_sms(phone: str, weeks: int) -> datetime:
    """Envia ya la confirmacion por SMS y deja programados en Mongo los
    recordatorios del dia anterior y del mismo dia de la cita, para que el
    scheduler (ver .scheduler) los envie cuando llegue su momento."""
    now = datetime.now(timezone.utc)
    appointment_date = now + timedelta(weeks=weeks)

    send_sms(phone, _message_for("confirmation", appointment_date))

    get_sms_reminders_collection().insert_many(
        [
            {
                "phone": phone,
                "kind": kind,
                "appointment_date": appointment_date,
                "send_at": send_at,
                "status": "pending",
                "created_at": now,
            }
            for kind, send_at in (
                ("day_before", appointment_date - timedelta(days=1)),
                ("same_day", appointment_date),
            )
        ]
    )
    return appointment_date


def send_due_reminders() -> int:
    """Busca en Mongo los recordatorios pendientes cuya fecha de envio ya ha
    llegado, los envia por SMS y los marca como enviados. Pensado para
    ejecutarse periodicamente desde el scheduler en background."""
    collection = get_sms_reminders_collection()
    now = datetime.now(timezone.utc)
    due = list(collection.find({"status": "pending", "send_at": {"$lte": now}}))

    for reminder in due:
        send_sms(reminder["phone"], _message_for(reminder["kind"], reminder["appointment_date"]))
        collection.update_one({"_id": reminder["_id"]}, {"$set": {"status": "sent", "sent_at": now}})

    return len(due)

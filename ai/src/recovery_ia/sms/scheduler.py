import logging

from apscheduler.schedulers.background import BackgroundScheduler

from .reminders import send_due_reminders

logger = logging.getLogger(__name__)

CHECK_INTERVAL_MINUTES = 15


def _run_due_reminders() -> None:
    sent = send_due_reminders()
    if sent:
        logger.info("Enviados %d recordatorios de SMS pendientes", sent)


def start_reminder_scheduler() -> BackgroundScheduler:
    """Arranca el job en background que revisa periodicamente los
    recordatorios de SMS pendientes (dia anterior / mismo dia de la cita) y
    los envia cuando les toca. Se llama una vez al arrancar la API."""
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(_run_due_reminders, "interval", minutes=CHECK_INTERVAL_MINUTES, id="send_due_sms_reminders")
    scheduler.start()
    return scheduler

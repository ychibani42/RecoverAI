from functools import lru_cache

from vonage import Auth, Vonage
from vonage_messages import Sms

from recovery_ia.config import get_settings


@lru_cache
def _get_client() -> Vonage:
    settings = get_settings()
    return Vonage(Auth(api_key=settings.vonage_api_key, api_secret=settings.vonage_api_secret))


def send_sms(to: str, text: str) -> None:
    settings = get_settings()
    _get_client().messages.send(Sms(to=to, from_=settings.vonage_sms_from, text=text))

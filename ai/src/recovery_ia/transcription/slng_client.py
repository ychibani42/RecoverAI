import httpx

from recovery_ia.config import get_settings

# Nova 3 "general" (no el nova:3-medical) porque este ultimo solo transcribe
# ingles; la app es principalmente en espanol/frances/ingles (ver i18n).
_STT_PATH = "/v1/stt/deepgram/nova:3"


def transcribe_audio(content: bytes, filename: str, content_type: str, language: str = "es") -> str:
    """Envia un audio a la Speech-to-Text API de SLNG (Deepgram Nova 3) y
    devuelve el texto transcrito."""
    settings = get_settings()
    url = f"https://{settings.slng_region}.api.slng.ai{_STT_PATH}"

    with httpx.Client(timeout=30.0) as client:
        response = client.post(
            url,
            headers={"Authorization": f"Bearer {settings.slng_api_key}"},
            files={"audio": (filename, content, content_type or "audio/webm")},
            data={"language": language},
        )

    if response.status_code >= 400:
        raise RuntimeError(f"SLNG transcription error {response.status_code}: {response.text}")

    payload = response.json()
    try:
        return payload["results"]["channels"][0]["alternatives"][0]["transcript"]
    except (KeyError, IndexError) as exc:
        raise RuntimeError(f"Respuesta inesperada de SLNG: {payload}") from exc

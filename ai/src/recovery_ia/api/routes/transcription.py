from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from recovery_ia.schemas import TranscriptionResponse
from recovery_ia.transcription import transcribe_audio

router = APIRouter(prefix="/transcription", tags=["transcription"])


@router.post("", response_model=TranscriptionResponse)
async def transcribe(
    audio: UploadFile = File(..., description="Audio grabado (dictado del informe medico)"),
    language: str = Form(default="es", description="Codigo de idioma (ISO 639-1) del audio"),
) -> TranscriptionResponse:
    """Transcribe un audio dictado por el clinico a texto, para rellenar el
    campo de informe medico sin tener que escribirlo."""
    content = await audio.read()
    try:
        text = transcribe_audio(content, audio.filename or "audio.webm", audio.content_type, language)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return TranscriptionResponse(text=text)

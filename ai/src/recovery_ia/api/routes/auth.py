import hmac

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from recovery_ia.api.security import issue_token
from recovery_ia.config.settings import get_settings

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    """Login del profesional que usa la herramienta (credencial unica configurada
    via ADMIN_USERNAME/ADMIN_PASSWORD en el .env)."""
    settings = get_settings()
    valid_username = hmac.compare_digest(payload.username, settings.admin_username)
    valid_password = hmac.compare_digest(payload.password, settings.admin_password)
    if not (valid_username and valid_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario o contraseña incorrectos")

    return LoginResponse(access_token=issue_token(payload.username))

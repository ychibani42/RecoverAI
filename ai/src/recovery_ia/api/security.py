import hmac
import time
from hashlib import sha256

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from recovery_ia.config.settings import get_settings

_bearer_scheme = HTTPBearer(auto_error=False)


def _sign(username: str, expires_at: int) -> str:
    settings = get_settings()
    payload = f"{username}:{expires_at}".encode()
    return hmac.new(settings.auth_secret_key.encode(), payload, sha256).hexdigest()


def issue_token(username: str) -> str:
    """Genera un token portador firmado (HMAC) con expiracion, sin dependencias
    externas de JWT: valido para el unico usuario profesional de la herramienta."""
    settings = get_settings()
    expires_at = int(time.time()) + settings.auth_token_ttl_hours * 3600
    signature = _sign(username, expires_at)
    return f"{username}.{expires_at}.{signature}"


def _verify_token(token: str) -> bool:
    try:
        username, expires_at_raw, signature = token.split(".", 2)
        expires_at = int(expires_at_raw)
    except ValueError:
        return False

    if time.time() > expires_at:
        return False

    expected_signature = _sign(username, expires_at)
    return hmac.compare_digest(signature, expected_signature)


def require_auth(credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme)) -> None:
    """Dependencia de FastAPI que protege las rutas clinicas: exige un token
    valido emitido por /auth/login en la cabecera Authorization: Bearer."""
    if credentials is None or not _verify_token(credentials.credentials):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado",
            headers={"WWW-Authenticate": "Bearer"},
        )
